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
    ) as cognito_service, patch("backend.flask.app.AuthService") as auth_service, patch(
        "backend.flask.app.DataService"
    ) as data_service, patch(
        "backend.flask.app.ShowService"
    ) as show_service, patch(
        "backend.flask.app.SongService"
    ) as song_service, patch(
        "backend.flask.app.DemoService"
    ) as demo_service:

        yield {
            "request": request_service,
            "cognito": cognito_service,
            "auth": auth_service,
            "data": data_service,
            "show": show_service,
            "song": song_service,
            "demo": demo_service,
        }


@pytest.fixture(scope="module")
def mock_external_libs() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("backend.flask.app.Flask") as mock_flask, patch(
        "backend.flask.app.CORS"
    ) as mock_cors, patch("backend.flask.app.JWTManager") as mock_jwt, patch(
        "backend.flask.app.JSONProvider"
    ) as mock_json_provider, patch(
        "backend.flask.app.logging"
    ) as mock_logging:

        yield {
            "flask": mock_flask,
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
        "backend.flask.app.RequestBlueprint"
    ) as request_blueprint, patch(
        "backend.flask.app.DemoBlueprint"
    ) as demo_blueprint, patch(
        "backend.flask.app.RenderBlueprint"
    ) as render_blueprint:

        yield {
            "user": user_blueprint,
            "data": data_blueprint,
            "auth": auth_blueprint,
            "show": show_blueprint,
            "song": song_blueprint,
            "request": request_blueprint,
            "render": render_blueprint,
            "demo": demo_blueprint,
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

    flask, cors, jwt_manager, json_provider, logging = (
        mock_external_libs["flask"],
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


# pylint: disable=protected-access
def test_when_create_app_then_blueprints_instantiated_with_services(
    mock_blueprints: Dict[str, MagicMock],
    mock_services: Dict[str, MagicMock],
) -> None:

    mock_blueprints["user"].assert_called_once_with(
        service=mock_services["cognito"].return_value, url_prefix="/api"
    )
    mock_blueprints["data"].assert_called_once_with(
        service=mock_services["data"].return_value, url_prefix="/api"
    )
    mock_blueprints["auth"].assert_called_once_with(
        service=mock_services["auth"].return_value, url_prefix="/api"
    )
    mock_blueprints["show"].assert_called_once_with(
        service=mock_services["show"].return_value, url_prefix="/api"
    )
    mock_blueprints["song"].assert_called_once_with(
        service=mock_services["song"].return_value, url_prefix="/api"
    )
    mock_blueprints["request"].assert_called_once_with(
        service=mock_services["request"].return_value
    )
    mock_blueprints["demo"].assert_called_once_with(
        service=mock_services["demo"].return_value
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
    flask_app.register_blueprint.assert_any_call(mock_blueprints["render"].return_value)
