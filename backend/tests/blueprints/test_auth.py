# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import json
from typing import Generator
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.auth import AuthBlueprint
from backend.flask.services.auth import AuthService

USERNAME = "username"
PASSWORD = "password"
SESSION = "session"
TOKEN = "token"


@pytest.fixture()
def app(service: AuthService) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(AuthBlueprint(service=service))
    yield app


@pytest.fixture()
def service() -> AuthService:
    return MagicMock(spec=AuthService)


def test_given_authenticate_user_returns_no_error_when_login_then_success_response_returned(
    client: FlaskClient, service: AuthService
) -> None:
    service.authenticate_user.return_value = {
        "token": TOKEN,
        "session": SESSION,
        "error": None,
    }

    response = client.post(
        "/login",
        json={
            "username": USERNAME,
            "password": PASSWORD,
        },
    )

    service.authenticate_user.assert_called_with(USERNAME, PASSWORD)

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data["token"] == TOKEN
    assert response_data["session"] == SESSION
    assert response_data["success"] is True
    assert response_data["error"] is None


def test_given_missing_creds_when_login_then_error_returned(
    client: FlaskClient,
) -> None:
    response = client.post("/login", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": "Username and password are required",
    }

    response = client.post("/login", json={"username": USERNAME})

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": "Username and password are required",
    }

    response = client.post("/login", json={"password": PASSWORD})

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": "Username and password are required",
    }


def test_given_password_reset_when_login_then_reset_password_called_and_returned(
    client: FlaskClient, service: AuthService
) -> None:
    service.reset_password.return_value = {
        "success": True,
        "token": TOKEN,
        "session": SESSION,
        "error": None,
    }

    response = client.post(
        "/login",
        json={
            "username": USERNAME,
            "password": PASSWORD,
            "session": SESSION,
            "password_reset": True,
        },
    )

    service.reset_password.assert_called_with(USERNAME, PASSWORD, SESSION)

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data["token"] == TOKEN
    assert response_data["session"] == SESSION
    assert response_data["success"] is True
    assert response_data["error"] is None
