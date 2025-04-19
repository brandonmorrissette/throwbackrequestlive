# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.config import Config

# App
ENVIRONMENT = MagicMock()
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


@pytest.fixture(autouse=True)
def boto_client() -> Generator[MagicMock, None, None]:
    with patch("boto3.client") as boto_client:
        boto_client.return_value.get_secret_value.return_value = {
            "SecretString": f"""{{
            "db_user": "{DB_USER}",
            "db_password": "{DB_PASSWORD}",
            "db_host": "{DB_HOST}",
            "db_name": "{DB_NAME}",
            "db_engine": "{DB_ENGINE}",
            "db_port": "{DB_PORT}"
            }}"""
        }
        yield boto_client


@pytest.fixture
def variables() -> Dict[str, Any]:
    return {
        name: value
        for name, value in globals().items()
        if not name.startswith("__") and name.isupper()
    }


# pylint: disable=invalid-name
def test_given_no_overrides_when_config_instantiated_then_config_set_to_default(
    variables: Dict[str, Any],
) -> None:
    with patch(
        "backend.flask.config.os.getenv",
        lambda key, default=None: variables.get(key, default),
    ):
        config = Config()

    # AWS
    assert config.AWS_DEFAULT_REGION == AWS_DEFAULT_REGION

    # App
    assert config.project_name == PROJECT_NAME
    assert config.debug == DEBUG
    assert config.log_level == LOG_LEVEL
    assert config.environment == ENVIRONMENT

    # JWT
    assert config.JWT_SECRET_KEY == JWT_SECRET_KEY
    assert config.JWT_TOKEN_LOCATION == JWT_TOKEN_LOCATION.split.return_value
    assert config.JWT_HEADER_NAME == JWT_HEADER_NAME
    assert config.JWT_HEADER_TYPE == JWT_HEADER_TYPE

    # Database
    assert config.db_user == DB_USER
    assert config.db_password == DB_PASSWORD
    assert config.db_host == DB_HOST
    assert config.db_name == DB_NAME
    assert config.db_engine == DB_ENGINE

    # Redis
    assert config.redis_host == REDIS_HOST
    assert config.redis_port == REDIS_PORT


def test_given_overrides_when_config_instantiated_then_overrirdes_set(
    variables: Dict[str, Any],
) -> None:
    debug = True
    variables["DEBUG"] = debug
    with patch(
        "backend.flask.config.os.getenv",
    ):
        config = Config()

    config = Config(**{key.lower(): value for key, value in variables.items()})

    # AWS
    assert config.AWS_DEFAULT_REGION == AWS_DEFAULT_REGION

    # App
    assert config.project_name == PROJECT_NAME
    assert config.debug == debug
    assert config.log_level == LOG_LEVEL

    # JWT
    assert config.JWT_SECRET_KEY == JWT_SECRET_KEY
    assert config.JWT_TOKEN_LOCATION == JWT_TOKEN_LOCATION.split.return_value
    assert config.JWT_HEADER_NAME == JWT_HEADER_NAME
    assert config.JWT_HEADER_TYPE == JWT_HEADER_TYPE

    # Database
    assert config.db_user == DB_USER
    assert config.db_password == DB_PASSWORD
    assert config.db_host == DB_HOST
    assert config.db_name == DB_NAME
    assert config.db_engine == DB_ENGINE

    # Redis
    assert config.redis_host == REDIS_HOST
    assert config.redis_port == REDIS_PORT


def test_given_no_environment_or_overrirdes_when_get_config_then_config_set_to_default() -> (
    None
):
    with patch.dict("os.environ", {}, clear=True):
        config = Config()

    # AWS
    assert config.AWS_DEFAULT_REGION is None

    # App
    assert config.project_name is None
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.environment == "local"

    # JWT
    assert config.JWT_SECRET_KEY is None
    assert config.JWT_TOKEN_LOCATION == ["headers"]
    assert config.JWT_HEADER_NAME == "Authorization"
    assert config.JWT_HEADER_TYPE == "Bearer"

    # Database
    assert config.db_user == ""
    assert config.db_password == ""
    assert config.db_host == ""
    assert config.db_name == ""
    assert config.db_engine == "postgresql+psycopg"
    assert config.db_port == "5432"

    # Redis
    assert config.redis_host == "redis"
    assert config.redis_port == "6379"


def test_given_secret_client_when_config_instantiated_then_secrets_retrieved(
    boto_client: MagicMock,
    variables: Dict[str, Any],
) -> None:
    with patch(
        "backend.flask.config.os.getenv",
        lambda key, default=None: variables.get(key, default),
    ):
        config = Config()
    boto_client.assert_called_once_with(
        "secretsmanager", region_name=AWS_DEFAULT_REGION
    )
    boto_client.return_value.get_secret_value.assert_called_once_with(
        SecretId=f"{config.project_name}-{config.environment}-db-credentials"
    )
