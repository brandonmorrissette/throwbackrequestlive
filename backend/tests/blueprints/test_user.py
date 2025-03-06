# pylint: disable=redefined-outer-name, protected-access
"""
Tests for the UserBlueprint in the Flask application.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from backend.flask.blueprints.user import UserBlueprint
from backend.flask.services.cognito import CognitoService
from backend.tests.mock.decorators import trace_decorator


@pytest.fixture(scope="module", autouse=True)
def mock_restrict_access():
    """Mock restrict_access while preserving function names."""

    mock_decorator, decorator_call_map = trace_decorator()

    with patch("backend.flask.blueprints.user.restrict_access", mock_decorator):
        yield decorator_call_map


@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""

    app = Flask(__name__)
    yield app


@pytest.fixture(scope="module")
def blueprint(app):
    """Set up the UserBlueprint."""

    return UserBlueprint(app)


@pytest.fixture()
def service():
    """Set up a mock of the CognitoService."""

    return MagicMock(spec=CognitoService)


@pytest.fixture()
def client(app, blueprint, service):
    """Set up a test client for making HTTP requests."""

    blueprint._service = service
    return app.test_client()


def test_given_request_when_read_rows_then_endpoint_is_restricted_to_superuser_group(
    client,
    mock_restrict_access,
):
    """Test that the read_rows route is restricted to the superuser group."""

    client.get("/users")
    assert mock_restrict_access["read_rows"] == ["superuser"]


def test_given_request_when_read_rows_then_users_returned(client, service):
    """Test the read_rows endpoint."""

    users = [{"username": "user1"}, {"username": "user2"}]
    service.read_rows.return_value = users

    response = client.get("/users")

    service.read_rows.assert_called_once()
    assert response.status_code == 200
    assert json.loads(response.data) == users


def test_given_request_when_write_rows_then_endpoint_is_restricted_to_superuser_group(
    client,
    mock_restrict_access,
):
    """Test that the write_rows route is restricted to the superuser group."""

    client.put("/users")
    assert mock_restrict_access["write_rows"] == ["superuser"]


def test_given_request_when_write_rows_then_success_response_returned(client, service):
    """Test the write_rows endpoint."""

    rows = [{"username": "user1"}]
    response_data = {"message": "Success"}
    service.write_rows.return_value = response_data

    response = client.put("/users", json={"rows": rows})

    service.write_rows.assert_called_once_with(rows)
    assert response.status_code == 200
    assert json.loads(response.data) == response_data


def test_given_invalid_request_when_write_rows_then_error_response_returned(client):
    """Test the write_rows endpoint with invalid input."""

    response = client.put("/users", json={})

    assert response.status_code == 400
    assert json.loads(response.data) == {
        "message": "Invalid input, rows not found in request."
    }
