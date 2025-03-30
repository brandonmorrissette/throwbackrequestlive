# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
from datetime import time

import pytest
from flask import Flask

from backend.flask.providers.json import JSONProvider


@pytest.fixture
def app():
    _app = Flask(__name__)
    _app.json_provider_class = JSONProvider
    _app.json = _app.json_provider_class(_app)
    return _app


def test_given_time_when_app_json_dumps_then_return_null(app):
    test_time = time(12, 34, 56)
    result = app.json.dumps(test_time)
    assert result == "null"


def test_given_time_in_dict_when_app_json_dumps_then_return_null_value_in_dict(app):
    test_dict = {"time": time(12, 34, 56)}
    result = app.json.dumps(test_dict)
    assert result == '{"time": null}'


def test_given_supported_type_when_app_json_dumps_then_return_value(app):
    test_dict = {"key": "value"}
    result = app.json.dumps(test_dict)
    assert result == '{"key": "value"}'
