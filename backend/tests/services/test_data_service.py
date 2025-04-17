# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
import copy
from typing import Dict, Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker as SessionMaker
from sqlalchemy.sql.schema import Table

from backend.flask.providers.sqlalchemy import SQLALchemyJSONProvider
from backend.flask.services.data import DataService, get_json_provider_class

TABLE_NAME = "table_name"
PRIMARY_KEY_NAME = "primary_key"
UUID = str(uuid4())


@pytest.fixture(autouse=True, scope="module")
def mock_app_logger() -> Generator[None, None, None]:
    with patch("backend.flask.services.data.app", new=MagicMock()):
        yield


@pytest.fixture()
def table(primary_key: MagicMock) -> MagicMock:
    table = MagicMock(spec=Table)
    table.name = TABLE_NAME
    # pylint:disable=no-member
    table.primary_key.columns.__iter__.return_value = [primary_key]
    return table


@pytest.fixture()
def primary_key() -> MagicMock:
    key = MagicMock()
    key.name = PRIMARY_KEY_NAME
    return key


@pytest.fixture()
def tables(table: MagicMock) -> Dict[str, MagicMock]:
    return {table.name: table}


@pytest.fixture()
def engine() -> Engine:
    return MagicMock()


@pytest.fixture()
def row() -> MagicMock:
    row = MagicMock()
    setattr(row, PRIMARY_KEY_NAME, UUID)
    row.get.side_effect = lambda key, default=None: {PRIMARY_KEY_NAME: UUID}.get(
        key, default
    )
    return row


@pytest.fixture
def session(row: MagicMock) -> MagicMock:
    session = MagicMock()
    session.query.return_value.all.return_value = [row]
    return session


@pytest.fixture
def sessionmaker(session: MagicMock) -> SessionMaker:
    return MagicMock(return_value=session)


@pytest.fixture
def metadata(tables: Dict[str, MagicMock]) -> MagicMock:
    metadata = MagicMock()
    metadata.tables = tables
    return metadata


@pytest.fixture
def app() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(
    config: MagicMock, metadata: MagicMock, engine: Engine, sessionmaker: SessionMaker
) -> DataService:
    with patch("backend.flask.services.data.create_engine", return_value=engine), patch(
        "backend.flask.services.data.sessionmaker", return_value=sessionmaker
    ), patch("backend.flask.services.data.MetaData", return_value=metadata), patch(
        "backend.flask.services.data.DataService._refresh_metadata"
    ):
        data_service = DataService(config)
        return data_service


def test_when_get_json_provider_class_is_called_then_return_sqlalchemy_json_provider() -> (
    None
):
    assert get_json_provider_class() == SQLALchemyJSONProvider


def test_given_successful_session_when_session_scope_then_session_managed(
    session: MagicMock, service: DataService
) -> None:
    with service._session_scope():
        pass

    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_given_sqlalchemy_error_when_session_scope_then_session_rollback(
    session: MagicMock, service: DataService
) -> None:
    session.commit.side_effect = SQLAlchemyError

    with patch.object(service, "_session", return_value=session):
        with pytest.raises(SQLAlchemyError):
            with service._session_scope():
                pass

    session.rollback.assert_called_once()
    session.close.assert_called_once()


def test_when_refresh_metadata_then_metadata_reflect_invoked(
    metadata: MagicMock, service: DataService, engine: Engine
) -> None:
    with patch.object(service, "_metadata", metadata):
        service._refresh_metadata()

    metadata.reflect.assert_called_once_with(bind=engine)


def test_given_table_when_get_primary_keys_then_primary_keys_returned(
    service: DataService, table: Table, primary_key: MagicMock
) -> None:
    assert service._get_primary_key_columns(table) == [primary_key.name]


def test_given_table_without_primary_keys_when_get_primary_keys_then_error_raised(
    service: DataService, table: Table
) -> None:
    table.primary_key.columns.__iter__.return_value = []

    with pytest.raises(ValueError):
        service._get_primary_key_columns(table)


def test_when_list_tables_then_return_table_names(
    service: DataService, tables: Dict[str, Table]
) -> None:
    with patch.object(service, "_refresh_metadata") as refresh_metadata:
        assert service.list_tables() == list(tables.keys())
        refresh_metadata.assert_called_once()


def test_given_table_name_when_get_table_then_table_returned(
    service: DataService, tables: Dict[str, Table]
) -> None:
    with patch.object(service, "_refresh_metadata") as refresh_metadata:
        table = service.get_table(TABLE_NAME)

    assert table == tables[TABLE_NAME]
    refresh_metadata.assert_called_once()


def test_given_non_existing_table_when_get_table_then_value_error_raised(
    service: DataService,
) -> None:
    with patch.object(service, "_refresh_metadata") as refresh_metadata:
        with pytest.raises(ValueError):
            service.get_table("non_existing_table")

    refresh_metadata.assert_called_once()


def test_given_existing_table_in_metadata_when_validate_then_continue(
    service: DataService,
) -> None:
    service.validate_table_name(TABLE_NAME)


def test_given_non_existing_table_when_validate_then_raise_value_error(
    service: DataService,
) -> None:
    with pytest.raises(ValueError):
        service.validate_table_name("non_existing_table")


def test_given_table_name_and_rows_when_insert_rows_then_insert_called(
    service: DataService, table: Table, session: Session
) -> None:
    rows = MagicMock()

    with patch.object(service, "_insert") as _insert:
        service.insert_rows(TABLE_NAME, rows)

    _insert.assert_called_once_with(table, rows, session)


def test_given_table_name_and_rows_without_keys_found_in_metadata_when_write_table_then_delete_called_with_keys(  # pylint:disable=line-too-long
    service: DataService, session: Session, table: Table
) -> None:
    with patch.object(service, "_delete") as _delete:
        service.write_table(TABLE_NAME, [])

    _delete.assert_called_once_with(table, {(UUID,)}, session)


def test_given_table_name_and_rows_already_in_metadata_when_write_table_then_insert_called_with_rows(  # pylint:disable=line-too-long
    service: DataService, session: Session, table: Table, row: MagicMock
) -> None:
    with patch.object(service, "_insert") as _insert:
        service.write_table(TABLE_NAME, [row])

    _insert.assert_called_once_with(table, [row], session)


def test_given_table_name_and_new_rows_when_write_table_then_insert_called_with_rows(
    service: DataService, session: Session, table: Table, row: MagicMock
) -> None:
    new = copy.deepcopy(row)
    new.get.side_effect = lambda key, default=None: {
        PRIMARY_KEY_NAME: str(uuid4())
    }.get(key, default)
    with patch.object(service, "_insert") as _insert:
        service.write_table(TABLE_NAME, [row])

    _insert.assert_called_once_with(table, [new], session)


def test_given_text_query_and_params_when_execute_then_converted_to_sql_text_and_executed(
    service: DataService, session: Session
) -> None:
    statement = "SELECT * FROM table_name WHERE id = :id"
    params = MagicMock()
    mapping = {MagicMock(): MagicMock()}
    result = MagicMock()
    result._mapping = mapping

    with patch.object(session, "execute") as execute, patch(
        "backend.flask.services.data.text"
    ) as text:
        execute.return_value = [result]
        response = service.execute(statement, params)

    text.assert_called_once_with(statement)
    execute.assert_called_once_with(text.return_value, params)
    assert response == [mapping]


def test_given_clause_element_query_and_params_when_execute_then_execute(
    service: DataService, session: Session
) -> None:
    statement = MagicMock()
    params = MagicMock()
    mapping = {MagicMock(): MagicMock()}
    result = MagicMock()
    result._mapping = mapping

    with patch.object(session, "execute") as execute, patch(
        "backend.flask.services.data.text"
    ) as text:
        execute.return_value = [result]
        response = service.execute(statement, params)

    text.assert_not_called()
    execute.assert_called_once_with(statement, params)
    assert response == [mapping]


def test_given_table_and_rows_when_insert_then_sql_alchemy_insert_invoked(
    service: DataService, table: Table, session: Session, row: MagicMock
) -> None:
    with patch.object(session, "execute") as execute, patch(
        "backend.flask.services.data.insert"
    ) as insert:
        service._insert(table, [row], session)

    insert.assert_called_once_with(table)
    insert.return_value.values.assert_called_once_with(**row.get.return_value)
    execute.assert_called_once_with(insert.return_value.values.return_value)


def test_given_table_and_rows_with_update_values_when_insert_then_on_conflict_do_update_invoked_and_executed(  # pylint:disable=line-too-long
    service: DataService, table: Table, session: Session, row: MagicMock
) -> None:
    column_name = MagicMock()
    column = MagicMock()
    column.name = column_name
    column.primary_key = False
    table.columns = [column]

    value = MagicMock()
    row.__getitem__.side_effect = lambda name: {column_name: value}.get(name, None)

    with patch.object(session, "execute") as execute, patch(
        "backend.flask.services.data.insert"
    ) as insert:
        service._insert(table, [row], session)

    insert.assert_called_once_with(table)
    insert.return_value.values.assert_called_once_with(**row.get.return_value)
    insert.return_value.values.return_value.on_conflict_do_update.assert_called_once_with(
        index_elements=[PRIMARY_KEY_NAME],
        set_={column_name: value},
    )
    execute.assert_called_once_with(
        insert.return_value.values.return_value.on_conflict_do_update.return_value
    )


def test_given_session_when_insert_then_execute_called_with_session(
    service: DataService, table: Table, session: Session, row: MagicMock
) -> None:
    with patch("backend.flask.services.data.insert") as insert:
        service._insert(table, [row], session)

    session.execute.assert_called_once_with(insert.return_value.values.return_value)


def test_given_no_session_when_insert_then_session_instantiated_and_execute_called(
    service: DataService, table: Table, row: MagicMock
) -> None:
    session = MagicMock()
    with patch("backend.flask.services.data.insert") as insert, patch.object(
        service, "_session_scope", return_value=session
    ):
        service._insert(table, [row])

    session.__enter__.return_value.execute.assert_called_once_with(
        insert.return_value.values.return_value
    )


def test_given_table_and_keys_and_session_when_delete_then_sql_alchemy_delete_invoked(
    service: DataService, table: Table, session: Session
) -> None:
    keys = {(UUID,)}

    with patch("backend.flask.services.data.tuple_") as tuple_:
        service._delete(table, keys, session)

    tuple_.assert_called_once_with(
        *[table.c[key] for key in service._get_primary_key_columns(table)]
    )
    tuple_.return_value.in_.assert_called_once_with(keys)
    table.delete.return_value.where.assert_called_once_with(
        tuple_.return_value.in_.return_value
    )
    session.execute.assert_called_once_with(
        table.delete.return_value.where.return_value
    )


def test_given_table_and_keys_and_no_session_when_delete_then_session_instantiated_and_execute_called(  # pylint:disable=line-too-long
    service: DataService, table: Table
) -> None:
    keys = {(UUID,)}

    session = MagicMock()
    with patch.object(service, "_session_scope", return_value=session):
        service._delete(table, keys)

    session.__enter__.return_value.execute.assert_called_once_with(
        table.delete.return_value.where.return_value
    )
