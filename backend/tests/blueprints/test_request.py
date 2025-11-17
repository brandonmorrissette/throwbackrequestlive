# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access

import json
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.exc import OperationalError

from backend.flask.blueprints.request import RequestBlueprint
from backend.flask.services.request import RequestService

UID = "uid"
SHOW_HASH = "show_hash"
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


def test_given_show_hash_when_redirect_request_then_redirect_is_returned(
    client: FlaskClient,
    service: RequestService,
) -> None:
    redirect = "redirect-url"
    service.redirect.return_value = redirect

    response = client.get(f"/requests/redirect/{SHOW_HASH}")

    assert response.get_data(as_text=True) == redirect
    assert response.status_code == 302


def test_given_redirect_raises_operational_error_when_redirect_request_then_redirect_to_main(
    client: FlaskClient,
    service: RequestService,
) -> None:
    service.redirect.side_effect = OperationalError(
        "OperationalError", None, Exception()
    )
    redirect = "render_main"
    with patch("backend.flask.blueprints.request.url_for") as mock_url_for:
        mock_url_for.return_value = redirect
        response = client.get(f"/requests/redirect/{SHOW_HASH}")

    assert response.status_code == 302
    assert response.location == redirect


def test_given_song_request_when_write_request_then_service_write_request_is_called(
    client: FlaskClient,
    service: RequestService,
) -> None:
    song_request = {"song_id": "song_id"}
    service.write_request.return_value = song_request

    response = client.post(
        "/requests",
        json=song_request,
    )

    assert response.status_code == 201
    assert response.get_json() == song_request
    service.write_request.assert_called_once_with(song_request)


def test_when_get_requests_count_then_service_get_requests_counts_is_called(
    client: FlaskClient,
    service: RequestService,
) -> None:
    counts = {"song_id": 5}
    service.get_requests_counts.return_value = counts

    response = client.get("/requests/count")

    assert response.status_code == 200
    assert response.get_json() == counts
    service.get_requests_counts.assert_called_once()
