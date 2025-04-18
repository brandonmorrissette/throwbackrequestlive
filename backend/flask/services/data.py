"""
Data service module for interacting with the database.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Set, Tuple, Union
from uuid import UUID

from flask import current_app as app
from sqlalchemy import MetaData, Table, create_engine, text, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement

from backend.flask.config import Config
from backend.flask.providers.sqlalchemy import SQLALchemyJSONProvider


def get_json_provider_class() -> type:
    """
    Get the JSON provider class.

    Returns:
        type: The JSON provider class.
    """
    return SQLALchemyJSONProvider


class DataService:
    """
    Service for interacting with the database.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the DataService.

        Args:
            config (Config): The configuration object.
        """

        database_url = (
            f"{config.db_engine}://"
            f"{config.db_user}:{config.db_password}@"
            f"{config.db_host}:{int(config.db_port)}/{config.db_name}"
        )

        logging.debug("Connecting to database: %s", database_url)
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._metadata = MetaData()
        self._session = sessionmaker(self._engine)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        self._refresh_metadata()

    @contextmanager
    def _session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        """
        app.logger.debug("Creating session")
        session = self._session()
        try:
            yield session
            app.logger.debug("Committing session")
            session.commit()
        except SQLAlchemyError as e:
            app.logger.error("Error in session: %s. Rolling back.", e)
            session.rollback()
            raise e
        finally:
            app.logger.debug("Closing session")
            session.close()

    def _refresh_metadata(self) -> None:
        """
        Refresh the metadata to reflect the current database schema.
        """
        self._metadata.reflect(bind=self._engine)

    def _get_primary_key_columns(self, table: Table) -> List[str]:
        """
        Get the primary key columns for a table.

        Args:
            table (Table): The SQLAlchemy table object.

        Returns:
            List[str]: A list of primary key column names.
        """
        primary_keys = [col.name for col in table.primary_key.columns]
        app.logger.debug("Primary keys for table %s: %s", table.name, primary_keys)
        if not primary_keys:
            raise ValueError(f"Table {table} has no primary key defined.")

        return primary_keys

    def list_tables(self) -> List[str]:
        """
        List all tables in the database.

        Returns:
            List[str]: A list of table names.
        """
        self._refresh_metadata()
        return list(self._metadata.tables.keys())

    def get_table(self, table_name: str) -> Table:
        """
        Get a table details by name.

        Args:
            table_name (str): The name of the table.

        Returns:
            Table: The SQLAlchemy Table object.
        """
        self._refresh_metadata()
        self.validate_table_name(table_name)
        table = self._metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        return table

    def validate_table_name(self, table_name: str) -> None:
        """
        Validate that a table name exists in the database.

        Args:
            table_name (str): The name of the table.

        Raises:
            ValueError: If the table does not exist.
        """
        if not self._metadata.tables or table_name not in self._metadata.tables:
            raise ValueError(f"Table {table_name} does not exist.")

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """
        Inserts rows to a table.

        Args:
            table_name (str): The name of the table.
            rows (List[Dict[str, Any]]): A list of dictionaries representing row data.
        """
        app.logger.debug("Adding rows to %s: %s", table_name, rows)
        if not rows:
            app.logger.debug("No rows to insert.")
            return

        table = self.get_table(table_name)
        with self._session_scope() as session:
            self._insert(table, rows, session)

    def write_table(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """
        Write a table to the database, replacing existing data completely.
        This method deletes existing rows that are not in the incoming data.

        Args:
            table_name (str): The name of the table.
            rows (List[Dict[str, Any]]): A list of dictionaries representing the rows to write.
        """
        table = self._metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist in metadata.")

        primary_key_columns = self._get_primary_key_columns(table)
        app.logger.debug(
            "Writing table %s with primary key columns %s",
            table_name,
            primary_key_columns,
        )

        incoming_keys = {
            tuple(UUID(row.get(key)) for key in primary_key_columns) for row in rows
        }
        app.logger.debug("Incoming keys: %s", incoming_keys)

        with self._session_scope() as session:
            existing_keys = {
                tuple(getattr(row, key) for key in primary_key_columns)
                for row in session.query(
                    *[table.c[key] for key in primary_key_columns]
                ).all()
            }
            app.logger.debug("Existing keys: %s", existing_keys)

            keys_to_delete = existing_keys - incoming_keys

            app.logger.debug("Keys to delete: %s", keys_to_delete)
            if keys_to_delete:
                self._delete(table, keys_to_delete, session)

            self._insert(
                table,
                rows,
                session,
            )

    def execute(
        self,
        statement: Union[str, ClauseElement],
        params: Union[Dict[str, Any], None] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL statement or SQLAlchemy Core expression.

        Args:
            statement (Union[str, ClauseElement]):
                 The SQL statement or SQLAlchemy Core expression to execute.
            params (Union[Dict[str, Any], None], optional): Parameters to bind to the SQL statement.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the query result.
        """
        if params is None:
            params = {}

        self._refresh_metadata()
        with self._session_scope() as session:
            if isinstance(statement, str):
                statement = text(statement)

            result = session.execute(statement, params)
            return [
                dict(row._mapping) for row in result  # pylint: disable=protected-access
            ]

    def _insert(
        self,
        table: Table,
        rows: List[Dict[str, Any]],
        session: Union[Session, None] = None,
    ) -> None:
        """
        Insert rows into a table with conflict resolution.

        Args:
            table (Table): The SQLAlchemy table object.
            rows (List[Dict[str, Any]]): A list of dictionaries representing the rows to insert.
            session (Union[Session, None], optional): An optional SQLAlchemy session.
        """

        def _execute(session: Session) -> None:
            primary_keys = self._get_primary_key_columns(table)
            for row in rows:
                stmt = insert(table).values(**row)
                update_values = {
                    col.name: row[col.name]
                    for col in table.columns
                    if not col.primary_key
                }
                if update_values:
                    stmt = stmt.on_conflict_do_update(
                        index_elements=primary_keys,
                        set_=update_values,
                    )
                session.execute(stmt)

        if session is None:
            with self._session_scope() as _session:
                _execute(_session)
        else:
            _execute(session)

    def _delete(
        self,
        table: Table,
        keys: Set[Tuple[Any, ...]],
        session: Union[Session, None] = None,
    ) -> None:
        """
        Delete rows from a table.

        Args:
            table (Table): The SQLAlchemy table object.
            keys (Set[Tuple[Any, ...]]): A set of keys to delete.
            session (Union[Session, None], optional): An optional SQLAlchemy session.
        """

        def _execute(session: Session) -> None:
            stmt = table.delete().where(
                tuple_(
                    *[table.c[key] for key in self._get_primary_key_columns(table)]
                ).in_(keys)
            )
            session.execute(stmt)

        if session is None:
            with self._session_scope() as _session:
                _execute(_session)
        else:
            _execute(session)
