"""
Data service module for interacting with the database.
"""

import json
import logging
from contextlib import contextmanager

import boto3
from flask import current_app as app
from sqlalchemy import MetaData, and_, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
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
        secrets_client = boto3.client(
            "secretsmanager", region_name=config.AWS_DEFAULT_REGION
        )
        secrets = json.loads(
            secrets_client.get_secret_value(
                SecretId=f"{config.project_name}-{config.environment}-db-credentials"
            )["SecretString"]
        )

        database_url = (
            f"{secrets["engine"]}://{secrets["username"]}:{secrets["password"]}@"
            f"{secrets["host"]}:{int(secrets["port"])}/{secrets["dbname"]}"
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

    def list_tables(self) -> list:
        """
        List all tables in the database.

        Returns:
            list: A list of table names.
        """
        self._refresh_metadata()
        return list(self._metadata.tables.keys())

    def get_table(self, table_name: str) -> dict:
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
        if table_name not in self._metadata.tables:
            raise ValueError(f"Table {table_name} does not exist.")

    def read_rows(self, table_name: str, filters: list | None = None) -> list:
        """
        Read rows from a table with optional filters.

        Args:
            table_name (str): The name of the table.
            filters (list, optional): A list of filter strings.

        Returns:
            list: A list of row dictionaries.
        """
        app.logger.debug("Reading rows from %s with filters: %s", table_name, filters)

        table = self.get_table(table_name)

        with self._session_scope() as session:
            query = session.query(table)

            if filters:
                filters_mapped = _map_filters(filters, table)
                app.logger.debug("Filters mapped: %s", filters_mapped)
                query = query.filter(*filters_mapped)

            app.logger.debug("Query: %s", query)
            return [row._asdict() for row in query.all()]

    def insert_rows(self, table_name: str, rows: list) -> None:
        """
        Inserts rows to a table.

        Args:
            table_name (str): The name of the table.
            rows (dict): A dictionary of row data.
        """
        app.logger.debug("Adding rows to %s: %s", table_name, rows)
        table = self.get_table(table_name)
        with self._session_scope() as session:
            session.execute(table.insert(), rows)

    def write_table(self, table_name: str, rows: list) -> None:
        """
        Write rows to a table.
        This assumes rows are the full data set.
        Any rows in the database that are not in the rows list will be deleted.

        Args:
            table_name (str): The name of the table.
            rows (list): A list of row dictionaries.
        """
        app.logger.debug("Write service invoked with %s: %s", table_name, rows)
        table = self.get_table(table_name)

        primary_keys = [col.name for col in table.primary_key.columns]
        if primary_keys is None:
            raise ValueError(
                f"Table {table_name} has no primary key defined. Unable to write rows."
            )

        with self._session_scope() as session:
            sql_alchemy_ids = {
                tuple(row)
                for row in session.query(*[table.c[col] for col in primary_keys]).all()
            }
            front_end_ids = {
                tuple(row[col] for col in primary_keys if col in row) for row in rows
            }
            app.logger.debug(
                "SQLAlchemy IDs: %s, Front-end IDs: %s", sql_alchemy_ids, front_end_ids
            )

            rows_to_add = [
                row
                for row in rows
                if any(row.get(col) is None for col in primary_keys)
                or tuple(row[col] for col in primary_keys) not in sql_alchemy_ids
            ]
            app.logger.debug("Rows to add: %s", rows_to_add)
            if rows_to_add:
                session.execute(table.insert(), rows_to_add)

            rows_to_delete = sql_alchemy_ids - front_end_ids
            app.logger.debug("Rows to delete: %s", rows_to_delete)
            if rows_to_delete:
                for key_tuple in rows_to_delete:
                    session.execute(
                        table.delete().where(
                            and_(
                                *[
                                    table.c[col] == key
                                    for col, key in zip(primary_keys, key_tuple)
                                ]
                            )
                        )
                    )

            rows_to_update = [
                row
                for row in rows
                if tuple(row.get(col) for col in primary_keys) in sql_alchemy_ids
            ]
            app.logger.debug("Rows to update: %s", rows_to_update)
            for row in rows_to_update:
                key_tuple = tuple(row[col] for col in primary_keys)
                session.execute(
                    table.update()
                    .where(
                        and_(
                            *[
                                table.c[col] == key
                                for col, key in zip(primary_keys, key_tuple)
                            ]
                        )
                    )
                    .values(**row)
                )

    def execute(self, statement: ClauseElement) -> list:
        """
        Execute a raw SQL statement.

        Args:
            statement (ClauseElement): The SQL statement to execute.
        """
        with self._session_scope() as session:
            result = session.execute(statement)
            return [dict(row) for row in result]


def _map_filters(filters: list, table) -> list:
    """
    Maps filter strings into SQLAlchemy filter expressions.

    Args:
        filters (list of str): List of filter strings like ["datetime >= 2024-12-28T00:00:00"].
        table (SQLAlchemy Table): The SQLAlchemy table to retrieve column objects from.

    Returns:
        list: List of SQLAlchemy filter expressions.
    """
    filter_expressions = []

    for filter_str in filters:
        try:
            column_name, operator, value = filter_str.split(maxsplit=2)
            app.logger.debug(
                "Column: %s, Operator: %s, Value: %s", column_name, operator, value
            )

            column = getattr(table.c, column_name)

            if operator == ">=":
                filter_expression = column >= value
            elif operator == "<=":
                filter_expression = column <= value
            elif operator == "=":
                filter_expression = column == value
            elif operator == ">":
                filter_expression = column > value
            elif operator == "<":
                filter_expression = column < value
            elif operator == "!=":
                filter_expression = column != value
            else:
                raise ValueError(f"Unsupported operator: {operator}")

            filter_expressions.append(filter_expression)

        except ValueError as e:
            raise ValueError(f"Invalid filter format: {filter_str}") from e

    return filter_expressions
