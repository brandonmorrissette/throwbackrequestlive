# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import json
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.show import ShowBlueprint
from backend.flask.services.entrypoint import EntryPointService
from backend.tests.mock.decorators import trace_decorator

show = {"name": "show"}


# Flask
@pytest.fixture(scope="module", autouse=True)
def mock_restrict_access() -> Generator[Dict[str, Any], None, None]:
    mock_decorator, decorator_call_map = trace_decorator()

    with patch("backend.flask.blueprints.show.restrict_access", mock_decorator):
        yield decorator_call_map


@pytest.fixture()
def app(blueprint: ShowBlueprint) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def blueprint(service: EntryPointService) -> ShowBlueprint:
    return ShowBlueprint(service=service)


@pytest.fixture()
def service() -> EntryPointService:
    return MagicMock(spec=EntryPointService)


def test_when_read_shows_then_all_shows_are_returned(
    client: FlaskClient, service: EntryPointService
) -> None:
    service.execute.return_value = [show]

    response = client.get("/tables/shows/rows")

    service.execute.assert_called_once_with("SELECT * FROM shows")
    assert response.status_code == 200
    assert json.loads(response.data) == [show]


def test_given_no_data_when_insert_show_then_error_is_returned(
    client: FlaskClient,
) -> None:
    response = client.post(
        "/tables/shows/rows", data=json.dumps({}), content_type="application/json"
    )

    assert response.status_code == 400
    assert json.loads(response.data) == {"message": "No data provided"}


def test_given_valid_data_when_insert_show_then_show_is_inserted(
    client: FlaskClient, service: EntryPointService
) -> None:
    entry_point_id = "entry_point_id"
    service.create_entrypoint.return_value = entry_point_id

    response = client.post(
        "/tables/shows/rows",
        data=json.dumps({"rows": [show]}),
        content_type="application/json",
    )

    show["entry_point_id"] = service.create_entrypoint.return_value
    service.insert_rows.assert_called_once_with("shows", [show])
    service.create_qr_code.assert_called_once_with(
        f"https://www.throwbackrequestlive.com/entrypoint?entryPointId={entry_point_id}",
        f"entrypoints/{show['name']}/",
    )
    assert response.status_code == 201
    assert json.loads(response.data) == {"success": True}


def test_when_get_upcoming_shows_then_upcoming_shows_are_returned(
    client: FlaskClient, service: EntryPointService
) -> None:
    service.execute.return_value = [show]

    response = client.get("/shows/upcoming")

    service.execute.assert_called_once_with(
        "SELECT * FROM shows WHERE start_time > NOW()::timestamp ORDER BY start_time ASC"
    )
    assert response.status_code == 200
    assert json.loads(response.data) == [show]
