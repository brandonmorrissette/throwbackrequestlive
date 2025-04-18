# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
import json
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.user import UserBlueprint
from backend.flask.services.cognito import CognitoService
from backend.tests.mock.decorators import trace_decorator


@pytest.fixture(autouse=True)
def mock_restrict_access() -> Generator[Dict[str, Any], None, None]:
    mock_decorator, decorator_call_map = trace_decorator()

    with patch("backend.flask.blueprints.user.restrict_access", mock_decorator):
        yield decorator_call_map


@pytest.fixture()
def app(service: CognitoService) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(UserBlueprint(service=service))

    yield app


@pytest.fixture()
def service() -> CognitoService:
    return MagicMock(spec=CognitoService)


def test_when_read_rows_then_endpoint_is_restricted_to_superuser_group(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.get("/users")
    assert mock_restrict_access["read_rows"] == ["superuser"]


def test_given_request_when_read_rows_then_users_returned(
    client: FlaskClient, service: CognitoService
) -> None:
    users: List[Dict[str, str]] = [{"username": "user1"}, {"username": "user2"}]
    service.read_rows.return_value = users

    response = client.get("/users")

    service.read_rows.assert_called_once()
    assert response.status_code == 200
    assert json.loads(response.data) == users


def test_given_request_when_write_rows_then_endpoint_is_restricted_to_superuser_group(
    client: FlaskClient,
    mock_restrict_access: Dict[str, Any],
) -> None:
    client.put("/users")
    assert mock_restrict_access["write_rows"] == ["superuser"]


def test_given_request_when_write_rows_then_success_response_returned(
    client: FlaskClient, service: CognitoService
) -> None:
    rows: List[Dict[str, str]] = [{"username": "user1"}]
    response_data: Dict[str, str] = {"message": "Success"}
    service.write_rows.return_value = response_data

    response = client.put("/users", json={"rows": rows})

    service.write_rows.assert_called_once_with(rows)
    assert response.status_code == 200
    assert json.loads(response.data) == response_data


def test_given_invalid_request_when_write_rows_then_error_response_returned(
    client: FlaskClient,
) -> None:
    response = client.put("/users", json={})

    assert response.status_code == 400
    assert json.loads(response.data) == {
        "message": "Invalid input, rows not found in request."
    }
