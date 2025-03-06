# pylint: disable=redefined-outer-name, protected-access
"""
Tests for the Blueprint class in the Flask application.
"""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from backend.flask.blueprints.blueprint import Blueprint


class TestBlueprint(Blueprint):  # pylint: disable=too-few-public-methods
    """A test class for the Blueprint."""

    def register_routes(self):
        """Register routes for the blueprint."""


@pytest.fixture()
def app():
    """Set up the Flask application for testing."""

    app = Flask(__name__)
    yield app


@pytest.fixture()
def service():
    """Set up a mock service."""

    return MagicMock()


@pytest.fixture()
def blueprint(app, service):
    """Set up the Blueprint."""

    return TestBlueprint(app, service=service)


def test_when_initialized_args_are_set(blueprint, service):
    """Test that the arguments are set correctly during initialization."""

    assert blueprint.name == "testblueprint"
    assert blueprint._service == service
    assert blueprint.url_prefix is None


def test_given_import_name_when_initialized_then_import_name_set(app, service):
    """Test that the import name is set correctly during initialization."""

    import_name = "testimportname"
    blueprint = TestBlueprint(app, import_name=import_name, service=service)
    assert blueprint.import_name == import_name


def test_when_init_then_blueprint_registered(app, service):
    """Test that the blueprint is registered with the Flask application."""

    blueprint = TestBlueprint(app, service=service)
    assert blueprint in app.blueprints.values()
