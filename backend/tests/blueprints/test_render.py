# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
from typing import Generator, Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.blueprints.render import RenderBlueprint

FILE = "<!DOCTYPE html><html><head><title>Test</title></head><body>Test</body></html>"


@pytest.fixture()
def app(tmpdir_factory: Any) -> Generator[Flask, None, None]:
    app = Flask(__name__)

    temp_static_dir = tmpdir_factory.mktemp("static")
    app.static_folder = str(temp_static_dir)

    index_file = temp_static_dir.join("index.html")
    index_file.write(FILE)

    app.register_blueprint(RenderBlueprint())

    yield app


def test_given_request_when_render_then_return_index(client: FlaskClient) -> None:
    response = client.get("/request")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_admin_when_render_then_return_index(client: FlaskClient) -> None:
    response = client.get("/admin")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_login_when_render_then_return_index(client: FlaskClient) -> None:
    response = client.get("/login")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_root_when_render_then_return_index(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_unregistered_when_reder_main_then_return_main_pageindex(
    client: FlaskClient,
) -> None:
    response = client.get("/some/random/path")
    assert response.status_code == 200
    assert FILE.encode() in response.data
