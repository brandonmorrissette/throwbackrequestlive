"""
Flask Application Module.

This module sets up and configures the Flask application, including logging,
services, and API blueprints. The application can be run in different environments
by setting the appropriate configuration.

Modules:
    logging
    os

Blueprints:
    AuthBlueprint
    DataBlueprint
    RenderBlueprint
    UserBlueprint

Configurations:
    Config
    DevelopmentConfig

Providers:
    JSONProvider

Services:
    AuthService
    CognitoService
    DataService

Functions:
    _create_app(config: Config) -> Flask: Creates and configures the Flask application.

Entry Point:
    The application can be run directly, and it will start the Flask server.
"""

import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.flask.blueprints.auth import RequestAuthBlueprint
from backend.flask.blueprints.data import DataBlueprint
from backend.flask.blueprints.render import RenderBlueprint
from backend.flask.blueprints.show import ShowBlueprint
from backend.flask.blueprints.song import SongBlueprint
from backend.flask.blueprints.user import UserBlueprint
from backend.flask.config import Config
from backend.flask.providers.json import JSONProvider
from backend.flask.services.auth import AuthService
from backend.flask.services.cognito import CognitoService
from backend.flask.services.data import DataService


def _create_app(app_config: Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        app_config (Config): The configuration object.

    Returns:
        Flask: The configured Flask application.
    """
    flask_app = Flask(__name__)

    CORS(flask_app, resources={r"/*": {"origins": "https://throwbackrequestlive.com"}})

    flask_app.json = JSONProvider(flask_app)
    flask_app.config.from_object(app_config)  # pylint: disable=no-member
    flask_app.logger.debug("Config : %s", flask_app.config)

    # Logging
    flask_app.logger.setLevel(app_config.log_level)
    logging.basicConfig(
        level=app_config.log_level,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )

    JWTManager(flask_app)

    # Services
    data_service = DataService(app_config)
    auth_service = AuthService(app_config)
    cognito_service = CognitoService(app_config)

    # API Blueprints
    flask_app.register_blueprint(
        RequestAuthBlueprint(service=auth_service, url_prefix="/api")
    )
    flask_app.register_blueprint(
        UserBlueprint(service=cognito_service, url_prefix="/api")
    )
    flask_app.register_blueprint(DataBlueprint(service=data_service, url_prefix="/api"))
    flask_app.register_blueprint(ShowBlueprint(service=data_service, url_prefix="/api"))
    flask_app.register_blueprint(SongBlueprint(service=data_service, url_prefix="/api"))

    # Render Blueprints
    flask_app.register_blueprint(RenderBlueprint())

    return flask_app


if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "").lower()
    logging.info("Flask App Environment: %s", environment)

    config = Config(environment)
    app = _create_app(config)
    app.run(host="0.0.0.0", port=5000, debug=config.debug)  # nosec B104
