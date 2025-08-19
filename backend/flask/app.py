"""
Flask Application Module.

This module sets up and configures the Flask application, including logging,
services, and API blueprints. The application can be run in different environments
by setting the appropriate configuration.
"""

import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.flask.blueprints.auth import AuthBlueprint
from backend.flask.blueprints.data import DataBlueprint
from backend.flask.blueprints.demo import DemoBlueprint
from backend.flask.blueprints.render import RenderBlueprint
from backend.flask.blueprints.request import RequestBlueprint
from backend.flask.blueprints.show import ShowBlueprint
from backend.flask.blueprints.song import SongBlueprint
from backend.flask.blueprints.user import UserBlueprint
from backend.flask.config import Config
from backend.flask.providers.json import JSONProvider
from backend.flask.services.auth import AuthService
from backend.flask.services.cognito import CognitoService
from backend.flask.services.data import DataService
from backend.flask.services.demo import DemoService
from backend.flask.services.request import RequestService
from backend.flask.services.show import ShowService
from backend.flask.services.song import SongService


def _create_app(app_config: Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        app_config (Config): The configuration object.

    Returns:
        Flask: The configured Flask application.
    """
    # App
    flask_app = Flask(__name__)
    flask_app.config.from_object(app_config)  # pylint: disable=no-member

    # Logging
    flask_app.logger.setLevel(app_config.log_level or "INFO")
    logging.basicConfig(
        level=app_config.log_level,
        format="%(asctime)s %(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s",
    )
    flask_app.logger.debug("App Config : %s", app_config.__dict__)
    flask_app.logger.debug("Flask Config : %s", flask_app.config)

    # JSON Provider
    flask_app.json = JSONProvider(flask_app)

    # CORS
    CORS(flask_app, resources={r"/*": {"origins": "https://throwbackrequestlive.com"}})

    # JWT
    JWTManager(flask_app)

    # API Blueprints (Restricted)
    flask_app.register_blueprint(
        UserBlueprint(service=CognitoService(app_config), url_prefix="/api")
    )
    flask_app.register_blueprint(
        DataBlueprint(service=DataService(app_config), url_prefix="/api")
    )

    # API Blueprints (Public - Login)
    flask_app.register_blueprint(
        AuthBlueprint(service=AuthService(app_config), url_prefix="/api")
    )

    # API Blueprints (Public)
    flask_app.register_blueprint(
        ShowBlueprint(service=ShowService(app_config), url_prefix="/api")
    )
    flask_app.register_blueprint(
        SongBlueprint(service=SongService(app_config), url_prefix="/api")
    )

    flask_app.register_blueprint(
        RequestBlueprint(service=RequestService(app_config)), url_prefix="/api"
    )
    flask_app.register_blueprint(DemoBlueprint(service=DemoService(app_config)))

    # Render Blueprints
    flask_app.register_blueprint(RenderBlueprint())

    return flask_app


if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "noenv").lower()
    logging.info("Flask App Environment: %s", environment)

    config = Config(environment)
    app = _create_app(config)
    app.run(host="0.0.0.0", port=5000, debug=config.debug)  # nosec B104
