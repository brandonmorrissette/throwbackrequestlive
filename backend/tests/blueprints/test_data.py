# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import json
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.data import DataBlueprint, override_json_provider
from backend.flask.services.data import DataService
from backend.tests.mock.decorators import trace_decorator


# Decorator
def test_given_callable_when_override_json_provider_then_provider_set() -> None:
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
def mock_restrict_access() -> Generator[Dict[str, Any], None, None]:
    mock_decorator, decorator_call_map = trace_decorator()

    with patch("backend.flask.blueprints.data.restrict_access", mock_decorator):
        yield decorator_call_map


@pytest.fixture()
def app(blueprint: DataBlueprint) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def blueprint(service: DataService) -> DataBlueprint:
    return DataBlueprint(service=service)


@pytest.fixture()
def service() -> DataService:
    return MagicMock(spec=DataService)


def test_when_list_tables_then_endpoint_is_restricted_to_appllicable_groups(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.get("/tables")
    assert mock_restrict_access["list_tables"] == ["superuser"]


def test_given_request_when_list_tables_then_return_tables(
    client: FlaskClient, service: DataService
) -> None:
    tables = ["table1", "table2"]
    service.list_tables.return_value = tables

    response = client.get("/tables")

    service.list_tables.assert_called_once()
    assert response.status_code == 200
    assert json.loads(response.data) == tables


def test_when_get_table_then_endpoint_is_restricted_to_appllicable_groups(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.get("/tables/table")
    assert mock_restrict_access["list_tables"] == ["superuser"]


def test_given_request_when_get_table_then_table_returned(
    client: FlaskClient, service: DataService
) -> None:
    table_data = {"data": "table_data"}
    service.get_table.return_value = table_data

    response = client.get("/tables/table")

    service.get_table.assert_called_once_with("table")

    assert response.status_code == 200
    assert json.loads(response.data) == table_data


def test_when_read_rows_then_endpoint_is_restricted_to_appllicable_groups(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.get("/tables/table/rows")
    assert mock_restrict_access["read_rows"] == ["superuser"]


def test_given_request_when_read_rows_then_table_data_returned(
    client: FlaskClient, blueprint: DataBlueprint
) -> None:
    with patch.object(blueprint, "_get_rows") as _get_rows:
        table_data = [{"data": "table_data"}]
        _get_rows.return_value = table_data

        response = client.get("/tables/table/rows")

        _get_rows.assert_called_once_with("table")

        assert response.status_code == 200
        assert json.loads(response.data) == table_data


def test_when_write_table_then_endpoint_is_restricted_to_appllicable_groups(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.put("/tables/table/rows")
    assert mock_restrict_access["write_table"] == ["superuser"]


def test_given_request_with_table_name_when_write_rows_then_table_name_is_validated(
    client: FlaskClient, blueprint: DataBlueprint
) -> None:
    table_name = "table"
    with patch.object(blueprint, "_service") as service:
        client.put(f"/tables/{table_name}/rows", json={"rows": []})
        service.validate_table_name.assert_called_once_with(table_name)


def test_given_request_when_write_table_then_success_response_returned(
    client: FlaskClient, blueprint: DataBlueprint
) -> None:
    with patch.object(blueprint, "_service") as service:
        rows = [{"data": "row_data"}]
        service.write_table.return_value = {"success": True}
        response = client.put("/tables/table/rows", json={"rows": rows})

        service.write_table.assert_called_once_with("table", rows)

        assert response.status_code == 200


def test_given_table_name_when_get_rows_then_table_name_validated(
    app: Flask, blueprint: DataBlueprint
) -> None:
    with patch.object(blueprint, "_service") as service:
        with app.app_context():
            service.execute.return_value = [{"success": True}]
            blueprint._get_rows("table")

            service.validate_table_name.assert_called_once_with("table")


def test_given_request_when_get_rows_then_rows_returned(
    app: Flask, blueprint: DataBlueprint
) -> None:
    with patch.object(blueprint, "_service") as service:
        with app.app_context():
            rows = [{"data": "row_data"}]
            service.execute.return_value = rows
            table_name = "table"
            response = blueprint._get_rows(table_name)

            service.execute.assert_called_once_with(f"SELECT * FROM {table_name}")

            assert response == rows
