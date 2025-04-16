# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, redefined-outer-name
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.flask.config import Config


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def config() -> Config:
    with patch("backend.flask.config.os"), patch("boto3.client"), patch(
        "backend.flask.config.json"
    ):
        _config = Config()
    return _config
