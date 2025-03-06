# pylint: disable=redefined-outer-name, protected-access
"""
Tests for the RenderBlueprint in the Flask application.
"""
import pytest
from flask import Flask

from backend.flask.blueprints.render import RenderBlueprint

FILE = "<!DOCTYPE html><html><head><title>Test</title></head><body>Test</body></html>"


@pytest.fixture(scope="module")
def app(tmpdir_factory):
    """Set up the Flask application for testing."""

    app = Flask(__name__)

    temp_static_dir = tmpdir_factory.mktemp("static")
    app.static_folder = str(temp_static_dir)

    index_file = temp_static_dir.join("index.html")
    index_file.write(FILE)
    yield app


@pytest.fixture(scope="module")
def blueprint(app):
    """Set up the RenderBlueprint."""

    return RenderBlueprint(app)


@pytest.fixture()
def client(app, blueprint):  # pylint: disable=unused-argument
    """Set up a test client for making HTTP requests."""

    return app.test_client()


def test_given_request_when_render_request_then_return_request_page(client):
    """Test the render_request endpoint."""

    response = client.get("/request")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_request_when_render_admin_then_return_admin_page(client):
    """Test the render_admin endpoint."""

    response = client.get("/admin")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_request_when_render_login_then_return_login_page(client):
    """Test the render_login endpoint."""

    response = client.get("/login")
    assert response.status_code == 200
    assert FILE.encode() in response.data


def test_given_request_when_render_main_then_return_main_page(client):
    """Test the render_main endpoint."""

    response = client.get("/")
    assert response.status_code == 200
    assert FILE.encode() in response.data

    response = client.get("/some/random/path")
    assert response.status_code == 200
    assert FILE.encode() in response.data
