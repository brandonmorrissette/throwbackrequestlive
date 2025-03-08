# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
import pytest
from flask import Flask

from backend.flask.blueprints.render import RenderBlueprint

FILE = "<!DOCTYPE html><html><head><title>Test</title></head><body>Test</body></html>"


@pytest.fixture()
def app(tmpdir_factory):
    app = Flask(__name__)

    temp_static_dir = tmpdir_factory.mktemp("static")
    app.static_folder = str(temp_static_dir)

    index_file = temp_static_dir.join("index.html")
    index_file.write(FILE)

    app.register_blueprint(RenderBlueprint())

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_given_request_when_render_then_return_index(client):
    response = client.get("/request")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_admin_when_render_then_return_index(client):
    response = client.get("/admin")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_login_when_render_then_return_index(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_root_when_render_then_return_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_unregistered_when_reder_main_then_return_main_pageindex(client):
    response = client.get("/some/random/path")
    assert response.status_code == 200
    assert FILE.encode() in response.data
