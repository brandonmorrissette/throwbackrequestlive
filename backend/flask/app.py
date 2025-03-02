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

from blueprints.auth import AuthBlueprint
from blueprints.data import DataBlueprint
from blueprints.render import RenderBlueprint
from blueprints.user import UserBlueprint
from config import Config, DevelopmentConfig
from flask import Flask
from flask_jwt_extended import JWTManager
from providers.json import JSONProvider
from services.auth import AuthService
from services.cognito import CognitoService
from services.data import DataService


def _create_app(app_config: Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        app_config (Config): The configuration object.

    Returns:
        Flask: The configured Flask application.
    """
    flask_app = Flask(__name__)
    flask_app.json = JSONProvider(flask_app)
    flask_app.config.from_object(app_config)
    flask_app.logger.debug("Config : %s", flask_app.config)

    # Logging
    flask_app.logger.setLevel(app_config.LOG_LEVEL)
    logging.basicConfig(
        level=app_config.LOG_LEVEL,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )

    JWTManager(flask_app)

    # Services
    auth_service = AuthService(app_config)
    cognito_service = CognitoService(app_config)
    data_service = DataService(app_config)

    # API Blueprints
    AuthBlueprint(flask_app, auth_service)
    UserBlueprint(flask_app, cognito_service)
    DataBlueprint(flask_app, data_service)

    # Render Blueprints
    RenderBlueprint(flask_app, url_prefix="")

    return flask_app


if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "").lower()
    logging.info("Flask App Environment: %s", environment)

    config = Config()
    if environment == "development":
        config = DevelopmentConfig()

    app = _create_app(config)
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
