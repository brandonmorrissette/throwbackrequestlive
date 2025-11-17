# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring, protected-access
import json
from typing import Generator
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.song import SongBlueprint
from backend.flask.services.song import SongService


@pytest.fixture()
def app(blueprint: SongBlueprint) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def blueprint(service: SongService) -> SongBlueprint:
    return SongBlueprint(service=service)


@pytest.fixture()
def service() -> SongService:
    return MagicMock(spec=SongService)


def test_when_read_songs_then_songs_are_returned(
    client: FlaskClient, service: SongService
) -> None:
    song = {"name": "song"}
    service.get_songs.return_value = [song]

    response = client.get("/songs")

    service.get_songs.assert_called_once()
    assert response.status_code == 200
    assert json.loads(response.data) == [song]
