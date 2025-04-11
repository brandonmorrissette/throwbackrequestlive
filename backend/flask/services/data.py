"""
Data service module for interacting with the database.
"""

import logging
from contextlib import contextmanager
from typing import Any

from flask import current_app as app
from sqlalchemy import MetaData, create_engine, text, tuple_
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
        self._metadata = MetaData(bind=self._engine)
        self._session = sessionmaker(bind=self._engine)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        self._refresh_metadata()

    @contextmanager
    def _session_scope(self):
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
        self._metadata.reflect()

    def _get_primary_keys(self, table: MetaData) -> list:
        """
        Get the primary keys for a table.

        Args:
            table (MetaData): The SQLAlchemy table object.

        Returns:
            list: A list of primary key column names.
        """
        primary_keys = [col.name for col in table.primary_key.columns]
        if not primary_keys:
            raise ValueError(f"Table {table} has no primary key defined.")

        return primary_keys

    def list_tables(self) -> list:
        """
        List all tables in the database.

        Returns:
            list: A list of table names.
        """
        self._refresh_metadata()
        return list(self._metadata.tables.keys())

    def get_table(self, table_name: str) -> MetaData:
        """
        Get a table by name.

        Args:
            table_name (str): The name of the table.

        Returns:
            dict: A dictionary representing the table schema.
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

    def insert_rows(self, table_name: str, rows: list) -> None:
        """
        Inserts rows to a table.

        Args:
            table_name (str): The name of the table.
            rows (dict): A dictionary of row data.
        """
        app.logger.debug("Adding rows to %s: %s", table_name, rows)
        if not rows:
            app.logger.debug("No rows to insert.")
            return

        table = self.get_table(table_name)
        with self._session_scope() as session:
            self._insert(table, rows, session)

    def write_table(self, table_name: str, rows: list[dict]) -> None:
        """
        Write a table to the database, replacing existing data completely.
        This method deletes existing rows that are not in the incoming data.

        Args:
            table_name (str): The name of the table.
            rows (list[dict]): A list of dictionaries representing the rows to write.
        """
        table = self._metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist in metadata.")

        primary_keys = self._get_primary_keys(table)
        app.logger.debug(
            "Writing table %s with primary keys %s", table_name, primary_keys
        )

        incoming_keys = {tuple(row.get(key) for key in primary_keys) for row in rows}
        app.logger.debug("Incoming keys: %s", incoming_keys)

        with self._session_scope() as session:
            keys_to_delete = {
                tuple(row)
                for row in session.query(*[table.c[key] for key in primary_keys]).all()
            } - incoming_keys

            app.logger.debug("Keys to delete: %s", keys_to_delete)
            if keys_to_delete:
                self._delete(table, keys_to_delete, session)

            self._insert(
                table,
                rows,
                session,
            )

    def execute(
        self, statement: str | ClauseElement, params: dict | None = None
    ) -> list:
        """
        Execute a raw SQL statement or SQLAlchemy Core expression.

        Args:
            statement (str | ClauseElement):
                The SQL statement or SQLAlchemy Core expression to execute.
            params (dict, optional): Parameters to bind to the SQL statement.

        Returns:
            list: A list of dictionaries representing the query result.
        """
        if params is None:
            params = {}
        with self._session_scope() as session:
            if isinstance(statement, str):
                statement = text(statement)

            result = session.execute(statement, params)
            return [dict(row) for row in result]

    def _insert(
        self,
        table: MetaData,
        rows: list[dict],
        session: Session | None = None,
    ) -> None:
        """
        Insert rows into a table with conflict resolution.

        Args:
            table (MetaData): The SQLAlchemy table object.
            rows (list[dict]): A list of dictionaries representing the rows to insert.
            session (Session, optional):
                An optional SQLAlchemy session.
                If not provided, a new session will be created.
        """

        def _execute(session):
            primary_keys = self._get_primary_keys(table)
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
        self, table: MetaData, keys: set[tuple[Any, ...]], session: Session | None
    ) -> None:
        """
        Delete rows from a table.

        Args:
            table (MetaData): The SQLAlchemy table object.
            keys (list): A list of keys to delete.
            session (Session, optional):
                An optional SQLAlchemy session.
                If not provided, a new session will be created.
        """

        def _execute(session):
            stmt = table.delete().where(
                tuple_(*[table.c[key] for key in self._get_primary_keys(table)]).in_(
                    keys
                )
            )
            session.execute(stmt)

        if session is None:
            with self._session_scope() as _session:
                _execute(_session)
        else:
            _execute(session)
