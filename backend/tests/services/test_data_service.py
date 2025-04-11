# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.flask.config import Config
from backend.flask.providers.sqlalchemy import SQLALchemyJSONProvider
from backend.flask.services.data import DataService, get_json_provider_class


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def metadata():
    return MagicMock()


@pytest.fixture
def config():
    mock_config = MagicMock(spec=Config)
    mock_config.__init__()  # pylint: disable=unnecessary-dunder-call
    return mock_config


@pytest.fixture
def service(config, metadata):
    with patch("backend.flask.services.data.create_engine") as mock_create_engine:
        mock_create_engine.return_value = MagicMock()
        data_service = DataService(config)
        data_service._metadata = metadata
        return data_service


def test_when_get_json_provider_class_is_called_then_return_sqlalchemy_json_provider():
    assert get_json_provider_class() == SQLALchemyJSONProvider


def test_given_successful_session_when_session_scope_then_session_managed(
    session,
    service,
):

    with patch.object(service, "_session", return_value=session):
        with service._session_scope():
            pass

    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_given_sqlalchemy_error_when_session_scope_then_session_rollback(
    session, service
):
    session.commit.side_effect = SQLAlchemyError

    with patch.object(service, "_session", return_value=session):
        with pytest.raises(SQLAlchemyError):
            with service._session_scope():
                pass

    session.rollback.assert_called_once()
    session.close.assert_called_once()


def test_when_refresh_metadata_then_metadata_reflect_invoked(metadata, service):
    with patch.object(service, "_metadata", metadata):
        service._refresh_metadata()

    metadata.reflect.assert_called_once()


def test_when_list_tables_then_return_table_names(service):
    table_names = ["table1", "table2"]
    service._metadata.tables = {name: MagicMock() for name in table_names}

    with patch.object(service, "_refresh_metadata") as refresh_metadata:
        assert service.list_tables() == table_names
        refresh_metadata.assert_called_once()


def test_given_existing_table_in_metadata_when_validate_then_continue(service):
    table_name = "table1"
    service._metadata.tables = {table_name: MagicMock()}

    service.validate_table_name(table_name)


def test_given_non_existing_table_when_validate_then_raise_value_error(
    service,
):
    with pytest.raises(ValueError):
        service.validate_table_name("table1")


def test_when_read_rows_then_metadata_refreshed(service):
    with patch.object(service, "_refresh_metadata") as refresh_metadata, patch.object(
        service, "_session_scope"
    ):
        service.read_rows("table1")
        refresh_metadata.assert_called_once()


def test_given_non_existing_table_name_when_read_rows_then_raise_value_error(
    metadata,
    service,
):
    metadata.tables.get.return_value = None
    with pytest.raises(ValueError):
        service.read_rows("table1")


def test_given_existing_table_name_when_read_rows_then_return_rows(service):
    row = MagicMock()

    with patch.object(service, "_session_scope") as session_scope:
        session_scope.return_value.__enter__.return_value.query.return_value.all.return_value = [
            row
        ]
        response = service.read_rows("table1")

    assert response == [row._asdict.return_value]


def test_given_filters_when_read_rows_then_filters_added_to_query(
    metadata,
    service,
):
    with patch.object(service, "_session_scope") as session_scope, patch(
        "backend.flask.services.data._map_filters"
    ) as map_filters:
        filters = MagicMock()
        map_filters.return_value = [filters]
        service.read_rows("table1", filters)
        map_filters.assert_called_once_with(filters, metadata.tables.get.return_value)
        session_scope.return_value.__enter__.return_value.query.return_value.filter.assert_called_once_with(  # pylint: disable=line-too-long
            map_filters.return_value[0]
        )


def test_given_session_when_read_rows_then_session_query_managed(metadata, service):
    with patch.object(service, "_session_scope") as session_scope:
        service.read_rows("table1")
        session_scope.return_value.__enter__.return_value.query.assert_called_once_with(
            metadata.tables.get.return_value
        )
        session_scope.return_value.__enter__.return_value.query.return_value.all.assert_called_once()  # pylint: disable=line-too-long


def test_when_write_rows_then_metadata_refreshed(metadata, service):
    with patch.object(service, "_refresh_metadata") as refresh_metadata, patch.object(
        service, "_session_scope"
    ):
        metadata.tables.get.return_value.primary_key.columns = [MagicMock()]
        service.write_rows("table1", [])
        refresh_metadata.assert_called_once()


def test_given_non_existing_table_name_when_write_rows_then_raise_value_error(
    metadata,
    service,
):
    metadata.tables.get.return_value = None
    with pytest.raises(ValueError):
        service.write_rows("table1", [])


def test_given_rows_not_in_table_when_write_rows_then_rows_added(
    metadata,
    service,
):
    primary_key = MagicMock()
    metadata.tables.get.return_value.primary_key.columns = [primary_key]
    row = MagicMock()
    row.get.return_value = None

    with patch.object(service, "_session_scope") as session_scope:
        service.write_rows("table1", [row])
        session_scope.return_value.__enter__.return_value.execute.assert_called_once_with(
            metadata.tables.get.return_value.insert.return_value, [row]
        )


def test_given_ids_in_sql_alchemy_not_present_in_rows_when_write_rows_then_delete_rows(
    metadata,
    service,
):
    primary_key = MagicMock()
    table = MagicMock()
    table.primary_key.columns = [primary_key]
    metadata.tables.get.return_value = table

    sql_alchemy_id = MagicMock()

    with patch.object(service, "_session_scope") as session_scope:
        session_scope.return_value.__enter__.return_value.query.return_value.all.return_value = [
            {primary_key.name: sql_alchemy_id}
        ]

        service.write_rows("table1", [])

        table.c[primary_key].in_.assert_called_once_with({sql_alchemy_id})
        table.delete.return_value.where.assert_called_once_with(
            table.c[primary_key].in_.return_value
        )
        session_scope.return_value.__enter__.return_value.execute.assert_called_with(
            table.delete.return_value.where.return_value
        )


def test_given_rows_to_update_when_write_rows_then_update_rows(
    metadata,
    service,
):
    primary_key = MagicMock()
    primary_key.name = "primary_key.name"
    table = MagicMock()
    table.primary_key.columns = [primary_key]
    metadata.tables.get.return_value = table

    sql_alchemy_id = MagicMock()
    row = {primary_key.name: sql_alchemy_id}

    with patch.object(service, "_session_scope") as session_scope:
        session_scope.return_value.__enter__.return_value.query.return_value.all.return_value = [
            {primary_key.name: sql_alchemy_id}
        ]

        service.write_rows("table1", [row])

        table.update.return_value.where.assert_called_once_with(
            table.c[primary_key] == sql_alchemy_id
        )
        table.update.return_value.where.return_value.values.assert_called_once_with(
            **row
        )
        session_scope.return_value.__enter__.return_value.execute.assert_called_with(
            table.update.return_value.where.return_value.values.return_value
        )
