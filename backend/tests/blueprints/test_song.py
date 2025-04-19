# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import json
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.song import SongBlueprint
from backend.flask.services.request import RequestService


@pytest.fixture()
def app(blueprint: SongBlueprint) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def blueprint(service: RequestService) -> SongBlueprint:
    return SongBlueprint(service=service)


@pytest.fixture()
def service() -> RequestService:
    return MagicMock(spec=RequestService)


def test_when_read_songs_then_songs_are_returned(client: FlaskClient) -> None:
    song = {"name": "song"}

    with patch(
        "backend.flask.blueprints.song.SongBlueprint._get_rows"
    ) as mock_get_rows:
        mock_get_rows.return_value = [song]

        response = client.get("/tables/songs/rows")

    mock_get_rows.assert_called_once_with("songs")
    assert response.status_code == 200
    assert json.loads(response.data) == [song]
