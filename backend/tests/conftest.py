# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, redefined-outer-name
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from backend.flask.config import Config


@pytest.fixture
def app() -> Flask:
    return Flask(__name__)


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


@pytest.fixture()
def mock_sql_alchemy_libraries(
    engine: MagicMock, session_maker: MagicMock, metadata: MagicMock
) -> Generator[None, None, None]:
    with patch("backend.flask.services.data.create_engine", return_value=engine), patch(
        "backend.flask.services.data.sessionmaker", return_value=session_maker
    ), patch("backend.flask.services.data.MetaData", return_value=metadata):
        yield


@pytest.fixture
def redis_client():
    return MagicMock()


@pytest.fixture()
def engine() -> Engine:
    return MagicMock()


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def session_maker(session: MagicMock) -> sessionmaker:
    return MagicMock(return_value=session)


@pytest.fixture
def metadata() -> MagicMock:
    return MagicMock()
