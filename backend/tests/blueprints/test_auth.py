# pylint: disable=redefined-outer-name, protected-access
"""
Tests for the AuthBlueprint in the Flask application.
"""

import json
from unittest.mock import MagicMock

import pytest
from flask import Flask

from services.auth import AuthService
from blueprints.auth import AuthBlueprint


@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""

    app = Flask(__name__)
    yield app


@pytest.fixture(scope="module")
def blueprint(app):
    """Set up the AuthBlueprint."""

    return AuthBlueprint(app)


@pytest.fixture()
def service():
    """Set up a mock of the AuthService."""

    return MagicMock(spec=AuthService)


@pytest.fixture()
def client(app, blueprint, service):
    """Set up a test client for making HTTP requests."""

    blueprint._service = service
    return app.test_client()


def test_given_success_when_login_then_response_returned(client, service):
    """Test the login endpoint with valid credentials."""

    token = "mock_token"
    session = "mock_session"

    service.authenticate_user.return_value = {
        "token": token,
        "session": session,
        "error": None,
    }

    response = client.post(
        "/login",
        data=json.dumps(
            {
                "username": "testuser",
                "password": "testpassword",
            }
        ),
        content_type="application/json",
    )

    service.authenticate_user.assert_called_with("testuser", "testpassword")

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data["token"] == token
    assert response_data["session"] == session
    assert response_data["success"] is True
    assert response_data["error"] is None


def test_given_missing_creds_when_login_then_error_returned(client):
    """Test the login endpoint with missing credentials."""

    response = client.post("/login", json={"username": "test"})

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": "Username and password are required",
    }


def test_given_password_reset_when_login_then_reset_password_called_and_returned(
    client, service
):
    """Test the login endpoint with a password reset request."""

    username = "testuser"
    password = "testpassword"
    session = "mock_session"
    token = "mock_token"

    return_value = {
        "success": True,
        "token": token,
        "session": session,
        "error": None,
    }
    service.reset_password.return_value = return_value

    response = client.post(
        "/login",
        json={
            "username": username,
            "password": password,
            "session": session,
            "password_reset": True,
        },
    )

    service.reset_password.assert_called_with(username, password, session)

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data["token"] == token
    assert response_data["session"] == session
    assert response_data["success"] is True
    assert response_data["error"] is None
