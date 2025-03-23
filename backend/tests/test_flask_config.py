# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.config import Config

DEBUG = False
LOG_LEVEL = MagicMock()

# JWT
JWT_SECRET_KEY = MagicMock()
JWT_TOKEN_LOCATION = MagicMock()
JWT_HEADER_NAME = MagicMock()
JWT_HEADER_TYPE = MagicMock()

# Cognito
COGNITO_APP_CLIENT_ID = MagicMock()
COGNITO_USER_POOL_ID = MagicMock()
COGNITO_REGION = MagicMock()

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
    assert config.debug == DEBUG
    assert config.log_level == LOG_LEVEL

    # JWT
    assert config.jwt_secret_key == JWT_SECRET_KEY
    assert config.jwt_token_location == JWT_TOKEN_LOCATION.split.return_value
    assert config.jwt_header_name == JWT_HEADER_NAME
    assert config.jwt_header_type == JWT_HEADER_TYPE

    # Cognito
    assert config.cognito_app_client_id == COGNITO_APP_CLIENT_ID
    assert config.cognito_user_pool_id == COGNITO_USER_POOL_ID
    assert config.cognito_region == COGNITO_REGION

    # Database
    assert config.db_user == DB_USER
    assert config.db_password == DB_PASSWORD
    assert config.db_host == DB_HOST
    assert config.db_name == DB_NAME
    assert config.db_engine == DB_ENGINE
    assert config.db_port == DB_PORT

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
    assert config.jwt_secret_key == JWT_SECRET_KEY
    assert config.jwt_token_location == JWT_TOKEN_LOCATION
    assert config.jwt_header_name == JWT_HEADER_NAME
    assert config.jwt_header_type == JWT_HEADER_TYPE

    # Cognito
    assert config.cognito_app_client_id == COGNITO_APP_CLIENT_ID
    assert config.cognito_user_pool_id == COGNITO_USER_POOL_ID
    assert config.cognito_region == COGNITO_REGION

    # Database
    assert config.db_user == DB_USER
    assert config.db_password == DB_PASSWORD
    assert config.db_host == DB_HOST
    assert config.db_name == DB_NAME
    assert config.db_engine == DB_ENGINE
    assert config.db_port == DB_PORT

    # Redis
    assert config.redis_host == REDIS_HOST
    assert config.redis_port == REDIS_PORT


def test_given_no_environment_or_overrirdes_when_get_config_then_config_set_to_default():
    with patch.dict("os.environ", {}, clear=True):
        config = Config()

    # App
    assert config.debug is False
    assert config.log_level == "INFO"

    # JWT
    assert config.jwt_secret_key is None
    assert config.jwt_token_location == ["headers"]
    assert config.jwt_header_name == "Authorization"
    assert config.jwt_header_type == "Bearer"

    # Cognito
    assert config.cognito_app_client_id is None
    assert config.cognito_user_pool_id is None
    assert config.cognito_region is None

    # Database
    assert config.db_user is None
    assert config.db_password is None
    assert config.db_host is None
    assert config.db_name is None
    assert config.db_engine == "postgresql"
    assert config.db_port == "5432"

    # Redis
    assert config.redis_host == "redis"
    assert config.redis_port == "6379"
