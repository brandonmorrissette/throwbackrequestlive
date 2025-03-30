# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
from unittest.mock import MagicMock

import pytest
from flask import Flask

from backend.flask.blueprints.blueprint import Blueprint


class TestBlueprint(
    Blueprint
):  # pylint: disable=too-few-public-methods, missing-class-docstring
    def register_routes(self):
        pass


@pytest.fixture()
def app(blueprint):
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app


@pytest.fixture()
def service():
    return MagicMock()


@pytest.fixture()
def blueprint(service):
    return TestBlueprint(service=service)


def test_when_initialized_args_are_set(blueprint, service):
    assert blueprint.name == blueprint.__class__.__name__.lower()
    assert blueprint._service == service  # pylint: disable=protected-access
    assert blueprint.url_prefix is None


def test_given_import_name_when_initialized_then_import_name_set(service):
    import_name = "testimportname"
    blueprint = TestBlueprint(import_name=import_name, service=service)
    assert blueprint.import_name == import_name
