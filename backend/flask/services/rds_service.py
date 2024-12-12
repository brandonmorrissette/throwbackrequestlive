import logging
from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


class RDSService:
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

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def refresh_metadata(self):
        self.metadata.reflect()

    def list_tables(self):
        self.refresh_metadata()
        return self.metadata.tables.keys()

    def get_columns(self, table_name):
        self.refresh_metadata()
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        return [
            {
                "name": column_name,
                "type": str(column.type),
                "nullable": column.nullable,
                "foreign_keys": [
                    {
                        "column": fk.column.name,
                        "table": fk.column.table.name,
                    }
                    for fk in column.foreign_keys
                ],
            }
            for column_name, column in table.columns.items()
        ]

    def validate_table_name(self, table_name):
        if table_name not in self.metadata.tables:
            raise ValueError(f"Table {table_name} does not exist.")

    def validate_columns(self, table_name, columns):
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        for column in columns:
            if column not in table.columns:
                raise ValueError(
                    f"Column {column} does not exist in table {table_name}."
                )

    def read_rows(
        self,
        table_name,
        filters=None,
        limit=None,
        offset=None,
        sort_by=None,
        sort_order="asc",
    ):
        self.refresh_metadata()
        table = self.metadata.tables.get(table_name)

        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        with self.session_scope() as session:
            query = session.query(table)
            if filters:
                query = query.filter_by(**filters)
            if sort_by:
                sort_column = getattr(table.c, sort_by)
                if sort_order == "desc":
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            return [row._asdict() for row in query.all()]

    def create_row(self, table_name, data):
        self.refresh_metadata()
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        with self.session_scope() as session:
            session.execute(table.insert().values(**data))

    def update_row(self, table_name, row_id, data):
        self.refresh_metadata()
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        primary_key = list(table.primary_key.columns)[0]
        with self.session_scope() as session:
            session.execute(table.update().where(primary_key == row_id).values(**data))

    def delete_row(self, table_name, row_id):
        self.refresh_metadata()
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist.")
        primary_key = list(table.primary_key.columns)[0]
        with self.session_scope() as session:
            session.execute(table.delete().where(primary_key == row_id))

    def execute_custom_query(self, query, params=None):
        with self.session_scope() as session:
            result = session.execute(query, params)
            return result.fetchall()

    def get_database_version(self):
        with self.session_scope() as session:
            version = session.execute("SELECT version()").scalar()
            return version
