# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import io
import json
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.request import RequestBlueprint
from backend.flask.services.request import RequestService

UID = "uid"
SHOW_ID = "show_id"
ENTRY_POINT_ID = "entry_point_id"

request = {"song_id": "song_id"}


@pytest.fixture()
def app(blueprint: RequestBlueprint) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def blueprint(service: RequestService) -> RequestBlueprint:
    return RequestBlueprint(service=service)


@pytest.fixture()
def service() -> RequestService:
    return MagicMock(spec=RequestService)


def test_given_request_with_bad_data_when_write_request_then_error_is_returned(
    client: FlaskClient,
) -> None:

    response = client.put(
        "/api/requests",
        data={},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "Invalid JSON data."}


def test_given_request_without_data_when_write_request_then_error_is_returned(
    client: FlaskClient,
) -> None:

    response = client.put(
        "/api/requests", data=json.dumps({}), content_type="application/json"
    )

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "No song request data found."}


def test_given_request_with_required_cookies_when_write_request_then_data_is_inserted(
    client: FlaskClient, service: RequestService
) -> None:

    with patch("backend.flask.blueprints.request.datetime") as mock_datetime:
        now = "2023-10-01T00:00:00Z"
        mock_datetime.now.return_value.isoformat.return_value = now

        client.set_cookie("uid", UID)
        client.set_cookie("showId", SHOW_ID)
        client.set_cookie("entryPointId", ENTRY_POINT_ID)

        service.insert_rows.return_value = {"success": True}

        request.update(
            {
                "id": UID,
                "show_id": SHOW_ID,
                "request_time": now,
            }
        )

        response = client.put(
            "/api/requests", data=json.dumps(request), content_type="application/json"
        )

        service.insert_rows.assert_any_call(
            "requests",
            [request],
        )
        service.insert_rows.assert_any_call(
            "submissions", [{"id": UID, "entry_point_id": ENTRY_POINT_ID}]
        )

        assert response.status_code == 200


def test_given_request_without_show_id_when_get_request_count_by_show_id_then_error_is_returned(
    client: FlaskClient,
) -> None:
    response = client.get("/api/requests/count")

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "No show ID provided."}


def test_given_show_id_when_get_request_count_by_show_id_then_count_is_returned(
    client: FlaskClient, service: RequestService
) -> None:
    count = {"count": 5}

    service.get_request_count_by_show_id.return_value = count

    response = client.get(f"/api/requests/count?showId={SHOW_ID}")

    service.get_request_count_by_show_id.assert_called_once_with(SHOW_ID)
    assert response.status_code == 200
    assert json.loads(response.data) == count


def test_when_demo_endpoint_then_redirect_to_render_request(
    client: FlaskClient, service: RequestService
) -> None:
    url = "/render_request"
    service.get_demo_entry_point_id.return_value = ENTRY_POINT_ID
    service.get_shows_by_entry_point_id.return_value = [
        {
            "id": SHOW_ID,
        }
    ]

    with patch("backend.flask.blueprints.request.url_for", return_value=url):
        response = client.get("/demo")

    service.get_demo_entry_point_id.assert_called_once()
    assert response.status_code == 302
    assert response.headers["Location"] == "/render_request"

    assert (
        "entryPointId=entry_point_id; Secure; HttpOnly; Path=/; SameSite=Lax"
        in response.headers.getlist("Set-Cookie")
    )
    assert (
        "showId=show_id; Secure; HttpOnly; Path=/; SameSite=Lax"
        in response.headers.getlist("Set-Cookie")
    )


def test_when_qr_then_qr_code_is_returned(
    client: FlaskClient, service: RequestService
) -> None:
    file = io.BytesIO(b"Mock Image")
    file.name = "mock_image.png"

    service.get_demo_qr.return_value = file

    response = client.get("/qr")
    assert response.status_code == 200
    assert response.data == file.getvalue()
