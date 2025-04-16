# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from backend.flask.app import _create_app


@pytest.fixture(scope="module")
def config() -> MagicMock:
    return MagicMock()


@pytest.fixture(scope="module")
def mock_services() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("backend.flask.app.RequestService") as request_service, patch(
        "backend.flask.app.CognitoService"
    ) as cognito_service, patch("backend.flask.app.AuthService") as auth_service:

        yield {
            "request": request_service,
            "cognito": cognito_service,
            "auth": auth_service,
        }


@pytest.fixture(scope="module")
def mock_external_libs() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("backend.flask.app.Flask") as mock_flask, patch(
        "backend.flask.app.CORS"
    ) as mock_cors, patch("backend.flask.app.JWTManager") as mock_jwt, patch(
        "backend.flask.app.JSONProvider"
    ) as mock_json_provider, patch(
        "backend.flask.app.redis.StrictRedis"
    ) as mock_redis, patch(
        "backend.flask.app.logging"
    ) as mock_logging:

        yield {
            "flask": mock_flask,
            "redis": mock_redis,
            "cors": mock_cors,
            "jwt": mock_jwt,
            "json_provider": mock_json_provider,
            "logging": mock_logging,
        }


@pytest.fixture(scope="module")
def mock_blueprints() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("backend.flask.app.UserBlueprint") as user_blueprint, patch(
        "backend.flask.app.DataBlueprint"
    ) as data_blueprint, patch(
        "backend.flask.app.AuthBlueprint"
    ) as auth_blueprint, patch(
        "backend.flask.app.ShowBlueprint"
    ) as show_blueprint, patch(
        "backend.flask.app.SongBlueprint"
    ) as song_blueprint, patch(
        "backend.flask.app.EntryPointBlueprint"
    ) as entrypoint_blueprint, patch(
        "backend.flask.app.RequestBlueprint"
    ) as request_blueprint, patch(
        "backend.flask.app.RenderBlueprint"
    ) as render_blueprint:

        yield {
            "user": user_blueprint,
            "data": data_blueprint,
            "auth": auth_blueprint,
            "show": show_blueprint,
            "song": song_blueprint,
            "entrypoint": entrypoint_blueprint,
            "request": request_blueprint,
            "render": render_blueprint,
        }


@pytest.fixture(autouse=True, scope="module")
def flask_app(
    # pylint: disable=unused-argument
    mock_services: Generator[Dict[str, MagicMock], None, None],
    mock_external_libs: Generator[Dict[str, MagicMock], None, None],
    mock_blueprints: Generator[Dict[str, MagicMock], None, None],
    config: MagicMock,
) -> Flask:
    return _create_app(config)


def test_config_when_create_app_then_flask_app_is_configured(
    flask_app: Flask,
    config: MagicMock,
    mock_external_libs: Dict[str, MagicMock],
) -> None:

    flask, redis, cors, jwt_manager, json_provider, logging = (
        mock_external_libs["flask"],
        mock_external_libs["redis"],
        mock_external_libs["cors"],
        mock_external_libs["jwt"],
        mock_external_libs["json_provider"],
        mock_external_libs["logging"],
    )

    # App
    assert flask_app == flask.return_value
    flask_app.config.from_object.assert_called_once_with(config)

    # Logging
    flask_app.logger.setLevel.assert_called_once_with(config.log_level)
    logging.basicConfig.assert_called_once_with(
        level=config.log_level,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )

    # JSON Provider
    json_provider.assert_called_once_with(flask.return_value)
    assert flask_app.json == json_provider.return_value

    # CORS
    cors.assert_called_once_with(
        flask_app, resources={r"/*": {"origins": "https://throwbackrequestlive.com"}}
    )

    # JWT
    jwt_manager.assert_called_once_with(flask_app)

    # Redis
    redis.assert_called_once_with(
        host=config.redis_host,
        port=int(config.redis_port),
        decode_responses=True,
    )


def test_given_config_when_create_app_then_config_is_set(
    config: MagicMock,
    mock_services: Dict[str, MagicMock],
    mock_external_libs: Dict[str, MagicMock],
) -> None:

    mock_services["auth"].assert_called_once_with(config)
    mock_services["cognito"].assert_called_once_with(
        mock_external_libs["redis"].return_value, config
    )
    mock_services["request"].assert_called_once_with(
        mock_external_libs["redis"].return_value, config
    )


# pylint: disable=protected-access
def test_given_services_when_create_app_then_services_injected_into_blueprints(
    mock_blueprints: Dict[str, MagicMock],
    mock_services: Dict[str, MagicMock],
) -> None:

    mock_blueprints["user"].assert_called_once_with(
        service=mock_services["cognito"].return_value, url_prefix="/api"
    )
    mock_blueprints["data"].assert_called_once_with(
        service=mock_services["request"].return_value, url_prefix="/api"
    )
    mock_blueprints["auth"].assert_called_once_with(
        service=mock_services["auth"].return_value, url_prefix="/api"
    )
    mock_blueprints["show"].assert_called_once_with(
        service=mock_services["request"].return_value, url_prefix="/api"
    )
    mock_blueprints["song"].assert_called_once_with(
        service=mock_services["request"].return_value, url_prefix="/api"
    )
    mock_blueprints["request"].assert_called_once_with(
        service=mock_services["request"].return_value
    )
    mock_blueprints["entrypoint"].assert_called_once_with(
        service=mock_services["request"].return_value
    )
    mock_blueprints["render"].assert_called_once_with()


def test_given_blueprints_when_create_app_then_blueprints_are_registered(
    flask_app: Flask,
    mock_blueprints: Dict[str, MagicMock],
) -> None:
    flask_app.register_blueprint.assert_any_call(mock_blueprints["user"].return_value)
    flask_app.register_blueprint.assert_any_call(mock_blueprints["data"].return_value)
    flask_app.register_blueprint.assert_any_call(mock_blueprints["auth"].return_value)
    flask_app.register_blueprint.assert_any_call(mock_blueprints["show"].return_value)
    flask_app.register_blueprint.assert_any_call(mock_blueprints["song"].return_value)
    flask_app.register_blueprint.assert_any_call(
        mock_blueprints["request"].return_value
    )
    flask_app.register_blueprint.assert_any_call(
        mock_blueprints["entrypoint"].return_value
    )
    flask_app.register_blueprint.assert_any_call(mock_blueprints["render"].return_value)
