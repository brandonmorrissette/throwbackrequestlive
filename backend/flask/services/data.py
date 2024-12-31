import logging
from contextlib import contextmanager

from providers.sqlalchemy import SQLALchemyJSONProvider
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


def get_json_provider_class():
    return SQLALchemyJSONProvider


class DataService:
    def __init__(self, config):
        DB_USER = config["database"]["DB_USER"]
        DB_PASSWORD = config["database"]["DB_PASSWORD"]
        DB_HOST = config["database"]["DB_HOST"]
        DB_NAME = config["database"]["DB_NAME"]
        DB_ENGINE = config["database"].get("DB_ENGINE", "postgresql")
        DB_PORT = config["database"].get("DB_PORT", 5432)

        DATABASE_URL = (
            f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        self.engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        self.metadata = MetaData(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._refresh_metadata()

    @contextmanager
    def _session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _refresh_metadata(self):
        self.metadata.reflect()

    def list_tables(self):
        self._refresh_metadata()
        return self.metadata.tables.keys()

    def get_table(self, table_name):
        self._refresh_metadata()
        self.validate_table_name(table_name)
        return self.metadata.tables.get(table_name)

    def validate_table_name(self, table_name):
        if table_name not in self.metadata.tables:
            raise ValueError(f"Table {table_name} does not exist.")

    def read_rows(self, table_name, filters=None):
        logging.debug(f"Reading rows from {table_name} with filters: {filters}")
        self._refresh_metadata()
        table = self.metadata.tables.get(table_name)

        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")

        with self._session_scope() as session:
            query = session.query(table)

            if filters:
                filters_mapped = _map_filters(filters, table)
                logging.debug(f"Filters mapped: {filters_mapped}")
                query = query.filter(*filters_mapped)

            logging.debug(f"Query: {query}")
            return [row._asdict() for row in query.all()]

    def write_rows(self, table_name, rows):
        self._refresh_metadata()
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")

        primary_key = list(table.primary_key.columns)[0].name
        with self._session_scope() as session:
            existing_ids = {
                row[primary_key] for row in session.query(table.c[primary_key]).all()
            }
            new_ids = {row[primary_key] for row in rows if primary_key in row}

            rows_to_delete = existing_ids - new_ids
            if rows_to_delete:
                session.execute(
                    table.delete().where(table.c[primary_key].in_(rows_to_delete))
                )

            new_rows = [row for row in rows if row[primary_key] not in existing_ids]
            if new_rows:
                session.execute(table.insert(), new_rows)

            rows_to_update = [row for row in rows if row[primary_key] in existing_ids]
            for row in rows_to_update:
                session.execute(
                    table.update()
                    .where(table.c[primary_key] == row[primary_key])
                    .values(**row)
                )

    def execute_custom_query(self, query, params=None):
        with self._session_scope() as session:
            result = session.execute(query, params)
            return result.fetchall()

    def get_database_version(self):
        with self._session_scope() as session:
            version = session.execute("SELECT version()").scalar()
            return version


def _map_filters(filters, table):
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
            logging.debug(
                f"Column: {column_name}, Operator: {operator}, Value: {value}"
            )

            column = getattr(table.c, column_name)

            # try:
            #     value = datetime.fromisoformat(value)
            #     logging.debug(f"Value is datetime: {value}")
            # except ValueError:
            #     pass

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

        except ValueError:
            raise ValueError(f"Invalid filter format: {filter_str}")

    return filter_expressions
