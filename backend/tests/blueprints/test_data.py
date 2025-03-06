# pylint: disable=redefined-outer-name, protected-access
"""
Tests for the DataBlueprint in the Flask application.
"""

import json
from unittest.mock import ANY, MagicMock, patch

import pytest
from blueprints.data import DataBlueprint, override_json_provider
from flask import Flask
from mock.decorators import trace_decorator
from services.data import DataService


# Decorator
def test_given_callable_when_override_json_provider_then_provider_set():
    """Test the override_json_provider decorator."""

    mock_app = MagicMock()
    mock_app_instance = MagicMock()

    mock_custom_provider = MagicMock()
    mock_original_provider = MagicMock()

    mock_app.json = mock_original_provider

    with patch("backend.flask.blueprints.data.app", mock_app), patch(
        "backend.flask.blueprints.data.Flask", return_value=mock_app_instance
    ):

        @override_json_provider(mock_custom_provider)
        def mock_callable():
            return "Success"

        result = mock_callable()

        mock_custom_provider.assert_called_once_with(mock_app_instance)
        assert mock_app.json == mock_original_provider

        assert result == "Success"


# Flask
@pytest.fixture(scope="module", autouse=True)
def mock_restrict_access():
    """Mock restrict_access while preserving function names."""

    mock_decorator, decorator_call_map = trace_decorator()

    with patch("backend.flask.blueprints.data.restrict_access", mock_decorator):
        yield decorator_call_map


@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""

    app = Flask(__name__)
    yield app


@pytest.fixture(scope="module")
def blueprint(app):
    """Set up the DataBlueprint."""

    return DataBlueprint(app)


@pytest.fixture()
def service():
    """Set up a mock of the DataService."""

    return MagicMock(spec=DataService)


@pytest.fixture()
def client(app, blueprint, service):
    """Set up a test client for making HTTP requests."""

    blueprint._service = service
    return app.test_client()


def test_given_request_when_list_tables_then_endpoint_is_restricted_to_appllicable_groups(
    client,
    mock_restrict_access,
):
    """Test that the list_tables route is restricted to the superuser group."""

    client.get("/tables")
    assert mock_restrict_access["list_tables"] == ["superuser"]


def test_given_request_when_list_tables_then_return_tables(client, service):
    """Test the list_tables endpoint."""

    tables = ["table1", "table2"]
    service.list_tables.return_value = tables

    response = client.get("/tables")

    service.list_tables.assert_called_once()
    assert response.status_code == 200
    assert json.loads(response.data) == tables


def test_given_request_when_get_table_then_endpoint_is_restricted_to_appllicable_groups(
    client,
    mock_restrict_access,
):
    """Test that the get_table route is restricted to the superuser group."""

    client.get("/tables/table")
    assert mock_restrict_access["list_tables"] == ["superuser"]


def test_given_request_when_get_table_then_table_returned(client, service):
    """Test the get_table endpoint."""

    table_data = {"data": "table_data"}
    service.get_table.return_value = table_data

    response = client.get("/tables/table")

    service.get_table.assert_called_once_with("table")

    assert response.status_code == 200
    assert json.loads(response.data) == table_data


def test_given_request_when_read_shows_then_endpoint_is_unrestricted(
    client,
    mock_restrict_access,
):
    """Test that the read_shows route is unrestricted."""

    client.get("/tables/shows/rows")
    assert "read_shows" not in mock_restrict_access


def test_given_request_when_read_shows_then_shows_returned(client, blueprint):
    """Test the read_shows endpoint."""

    with patch.object(blueprint, "_get_rows") as _get_rows:
        shows_data = [{"data": "shows_data"}]
        _get_rows.return_value = shows_data

        response = client.get("/tables/shows/rows")

        _get_rows.assert_called_once_with("shows", ANY)

        assert response.status_code == 200
        assert json.loads(response.data) == shows_data


def test_given_request_when_read_rows_then_endpoint_is_restricted_to_appllicable_groups(
    client,
    mock_restrict_access,
):
    """Test that the read_rows route is restricted to the superuser group."""

    client.get("/tables/table/rows")
    assert mock_restrict_access["read_rows"] == ["superuser"]


def test_given_request_when_read_rows_then_table_data_returned(client, blueprint):
    """Test the read_rows endpoint."""

    with patch.object(blueprint, "_get_rows") as _get_rows:
        table_data = [{"data": "table_data"}]
        _get_rows.return_value = table_data

        response = client.get("/tables/table/rows")

        _get_rows.assert_called_once_with("table", ANY)

        assert response.status_code == 200
        assert json.loads(response.data) == table_data


def test_given_request_when_write_rows_then_endpoint_is_restricted_to_appllicable_groups(
    client,
    mock_restrict_access,
):
    """Test that the write_rows route is restricted to the superuser group."""

    client.put("/tables/table/rows")
    assert mock_restrict_access["write_rows"] == ["superuser"]


def test_given_request_with_table_name_when_write_rows_then_table_name_is_validated(
    client, blueprint
):
    """Test that the table name is validated in the write_rows method."""

    with patch.object(blueprint, "_service") as service:
        client.put("/tables/table/rows", json={"rows": []})
        service.validate_table_name.assert_called_once_with("table")


def test_given_request_when_write_rows_then_success_response_returned(
    client, blueprint
):
    """Test the write_rows endpoint."""

    with patch.object(blueprint, "_service") as service:
        rows = [{"data": "row_data"}]
        service.write_rows.return_value = {"success": True}
        response = client.put("/tables/table/rows", json={"rows": rows})

        service.write_rows.assert_called_once_with("table", rows)

        assert response.status_code == 200


def test_given_filters_when_get_rows_then_filters_applied(app, blueprint):
    """Test that the filters are applied in the _get_rows method."""

    with patch.object(blueprint, "_service") as service:
        filters = '{"data": "filter_data"}'
        request = MagicMock(args={"filters": filters})
        with app.app_context():
            service.read_rows.return_value = [{"success": True}]
            blueprint._get_rows("table", request)

            service.read_rows.assert_called_once_with("table", json.loads(filters))


def test_given_table_name_and_request_when_get_rows_then_table_name_validated(
    app, blueprint
):
    """Test that the table name is validated in the _get_rows method."""

    with patch.object(blueprint, "_service") as service:
        request = MagicMock(args={})
        with app.app_context():
            service.read_rows.return_value = [{"success": True}]
            blueprint._get_rows("table", request)

            service.validate_table_name.assert_called_once_with("table")


def test_given_request_when_get_rows_then_rows_returned(app, blueprint):
    """Test the _get_rows method return value."""

    with patch.object(blueprint, "_service") as service:
        request = MagicMock(args={})
        with app.app_context():
            rows = [{"data": "row_data"}]
            service.read_rows.return_value = rows
            response, status_code = blueprint._get_rows("table", request)

            service.read_rows.assert_called_once_with("table", None)

            assert status_code == 200
            assert response.status_code == 200
            assert json.loads(response.data) == rows
