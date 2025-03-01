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


def _create_app(config: Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config (Config): The configuration object.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    app.json = JSONProvider(app)
    app.config.from_object(config)
    app.logger.debug(f"Config : {app.config}")

    # Logging
    app.logger.setLevel(config.LOG_LEVEL)
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )

    JWTManager(app)

    # Services
    auth_service = AuthService(config)
    cognito_service = CognitoService(config)
    data_service = DataService(config)

    # API Blueprints
    AuthBlueprint(app, auth_service)
    UserBlueprint(app, cognito_service)
    DataBlueprint(app, data_service)

    # Render Blueprints
    RenderBlueprint(app, url_prefix="")

    return app


if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "").lower()
    logging.info(f"Flask App Environment: {environment}")

    config = Config
    if environment == "development":
        config = DevelopmentConfig

    app = _create_app(config)
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
