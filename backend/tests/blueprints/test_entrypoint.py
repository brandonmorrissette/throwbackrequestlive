# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.entrypoint import EntryPointBlueprint
from backend.flask.services.entrypoint import EntryPointService

ENTRYPOINT_ID = "entrypoint_id"
TOKEN = "token"
RESPONSE = {"Response": "response"}


@pytest.fixture()
def app(service: EntryPointService) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(EntryPointBlueprint(service=service))
    return app


@pytest.fixture()
def service() -> EntryPointService:
    return MagicMock(spec=EntryPointService)


def test_given_entrypoint_id_when_start_session_then_start_session_invoked(
    client: FlaskClient, service: EntryPointService
) -> None:
    service.start_session.return_value = RESPONSE
    response = client.get(f"/entrypoint?entryPointId={ENTRYPOINT_ID}")

    service.start_session.assert_called_with(ENTRYPOINT_ID)
    assert response.status_code == 200
    assert response.get_json() == RESPONSE


def test_given_valid_session_when_validate_then_validate_session_invoked(
    client: FlaskClient, service: EntryPointService
) -> None:
    service.validate_session.return_value = RESPONSE
    response = client.get("/validate")

    service.validate_session.assert_called_once()
    assert response.status_code == 200
    assert response.get_json() == RESPONSE
