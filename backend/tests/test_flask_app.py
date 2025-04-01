# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.app import _create_app
from backend.flask.blueprints.auth import RequestAuthBlueprint
from backend.flask.blueprints.data import DataBlueprint
from backend.flask.blueprints.render import RenderBlueprint
from backend.flask.blueprints.user import UserBlueprint
from backend.flask.config import Config


@pytest.fixture
def config():
    return Config()


@pytest.fixture(autouse=True)
def mock_services():
    auth_service = MagicMock()
    user_service = MagicMock()
    data_service = MagicMock()

    with patch("backend.flask.app.AuthService", return_value=auth_service), patch(
        "backend.flask.app.CognitoService", return_value=user_service
    ), patch("backend.flask.app.DataService", return_value=data_service):

        yield {
            "auth_service": auth_service,
            "user_service": user_service,
            "data_service": data_service,
        }


def test_config_when_create_app_then_flask_app_is_configured():
    config = MagicMock()

    with patch("backend.flask.app.Flask") as flask, patch(
        "backend.flask.app.JSONProvider"
    ) as json_provider, patch("backend.flask.app.logging") as logging, patch(
        "backend.flask.app.JWTManager"
    ) as jwt_manager:

        flask_app = _create_app(config)

    assert flask_app == flask.return_value

    json_provider.assert_called_once_with(flask.return_value)
    assert flask_app.json == json_provider.return_value
    flask_app.config.from_object.assert_called_once_with(  # pylint: disable=no-member
        config
    )
    flask_app.logger.setLevel.assert_called_once_with(config.log_level)
    logging.basicConfig.assert_called_once_with(
        level=config.log_level,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )
    jwt_manager.assert_called_once_with(flask_app)


def test_given_config_when_create_app_then_config_is_set(config):
    with patch("backend.flask.app.AuthService") as auth_service, patch(
        "backend.flask.app.CognitoService",
    ) as user_service, patch("backend.flask.app.DataService") as data_service:
        _create_app(config)

    auth_service.assert_called_once_with(config)
    user_service.assert_called_once_with(config)
    data_service.assert_called_once_with(config)


# pylint: disable=protected-access
def test_given_services_when_create_app_then_services_injected_into_blueprints(
    mock_services, config
):
    app = _create_app(config)

    assert app.blueprints["authblueprint"]._service == mock_services["auth_service"]
    assert app.blueprints["userblueprint"]._service == mock_services["user_service"]
    assert app.blueprints["datablueprint"]._service == mock_services["data_service"]


def test_given_blueprints_when_create_app_then_blueprints_are_registered(config):
    app = _create_app(config)

    assert isinstance(app.blueprints["authblueprint"], RequestAuthBlueprint)
    assert isinstance(app.blueprints["userblueprint"], UserBlueprint)
    assert isinstance(app.blueprints["datablueprint"], DataBlueprint)
    assert isinstance(app.blueprints["renderblueprint"], RenderBlueprint)
