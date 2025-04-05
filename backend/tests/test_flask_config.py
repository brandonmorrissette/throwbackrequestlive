# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.config import Config

# App
PROJECT_NAME = MagicMock()
DEBUG = False
LOG_LEVEL = MagicMock()

# JWT
JWT_SECRET_KEY = MagicMock()
JWT_TOKEN_LOCATION = MagicMock()
JWT_HEADER_NAME = MagicMock()
JWT_HEADER_TYPE = MagicMock()

# AWS
AWS_DEFAULT_REGION = MagicMock()

# Database
DB_USER = MagicMock()
DB_PASSWORD = MagicMock()
DB_HOST = MagicMock()
DB_NAME = MagicMock()
DB_ENGINE = MagicMock()
DB_PORT = MagicMock()

# Redis
REDIS_HOST = MagicMock()
REDIS_PORT = MagicMock()


@pytest.fixture
def variables():
    return {
        name: value
        for name, value in globals().items()
        if not name.startswith("__") and name.isupper()
    }


# pylint: disable=invalid-name
def test_given_no_overrides_when_config_instantiated_then_config_set_to_default(
    variables,
):
    with patch(
        "backend.flask.config.os.getenv",
        lambda key, default=None: variables.get(key, default),
    ):
        config = Config()

    # App
    assert config.project_name == PROJECT_NAME
    assert config.debug == DEBUG
    assert config.log_level == LOG_LEVEL

    # JWT
    assert config.JWT_SECRET_KEY == JWT_SECRET_KEY
    assert config.JWT_TOKEN_LOCATION == JWT_TOKEN_LOCATION.split.return_value
    assert config.JWT_HEADER_NAME == JWT_HEADER_NAME
    assert config.JWT_HEADER_TYPE == JWT_HEADER_TYPE

    # AWS
    assert config.AWS_DEFAULT_REGION == AWS_DEFAULT_REGION

    # Redis
    assert config.redis_host == REDIS_HOST
    assert config.redis_port == REDIS_PORT


def test_given_overrides_when_config_instantiated_then_overrirdes_set(variables):
    debug = True
    variables["DEBUG"] = debug
    with patch(
        "backend.flask.config.os.getenv",
    ):
        config = Config()

    config = Config(**{key.lower(): value for key, value in variables.items()})

    # App

    assert config.debug == debug
    assert config.log_level == LOG_LEVEL

    # JWT
    assert config.JWT_SECRET_KEY == JWT_SECRET_KEY
    assert config.JWT_TOKEN_LOCATION == JWT_TOKEN_LOCATION
    assert config.JWT_HEADER_NAME == JWT_HEADER_NAME
    assert config.JWT_HEADER_TYPE == JWT_HEADER_TYPE

    # Cognito
    assert config.AWS_DEFAULT_REGION == AWS_DEFAULT_REGION

    # Redis
    assert config.redis_host == REDIS_HOST
    assert config.redis_port == REDIS_PORT


def test_given_no_environment_or_overrirdes_when_get_config_then_config_set_to_default():
    with patch.dict("os.environ", {}, clear=True):
        config = Config()

    # App
    assert config.project_name is None
    assert config.debug is False
    assert config.log_level == "INFO"

    # JWT
    assert config.JWT_SECRET_KEY is None
    assert config.JWT_TOKEN_LOCATION == ["headers"]
    assert config.JWT_HEADER_NAME == "Authorization"
    assert config.JWT_HEADER_TYPE == "Bearer"

    # Cognito
    assert config.AWS_DEFAULT_REGION is None

    # Redis
    assert config.redis_host == "redis"
    assert config.redis_port == "6379"
