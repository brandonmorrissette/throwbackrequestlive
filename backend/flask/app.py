import logging
import os
from datetime import time

from blueprints.auth import AuthBlueprint
from blueprints.data import DataBlueprint
from blueprints.render import RenderBlueprint
from blueprints.user import UserBlueprint
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_jwt_extended import JWTManager
from services.auth import AuthService
from services.cognito import CognitoService
from services.data import DataService

CONFIG = {
    "jwt": {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
    },
    "cognito": {
        "COGNITO_APP_CLIENT_ID": os.getenv("COGNITO_APP_CLIENT_ID"),
        "COGNITO_USER_POOL_ID": os.getenv("COGNITO_USER_POOL_ID"),
        "COGNITO_REGION": os.getenv("COGNITO_REGION"),
    },
    "database": {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_ENGINE": os.getenv("DB_ENGINE", "postgresql"),
        "DB_PORT": os.getenv("DB_PORT", 5432),
    },
    "redis": {
        "REDIS_HOST": os.getenv("REDIS_HOST", "redis"),
        "REDIS_PORT": os.getenv("REDIS_PORT", 6379),
    },
}


class JSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return None
        return super().default(obj)


def _create_app():
    app = Flask(__name__)
    app.json = JSONProvider(app)
    app.logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    for current in CONFIG:
        app.config.update(CONFIG[current])
    app.logger.debug(f"Config : {app.config}")

    JWTManager(app)

    # Services
    auth_service = AuthService(CONFIG)
    cognito_service = CognitoService(CONFIG)
    data_service = DataService(CONFIG)

    # API Blueprints
    AuthBlueprint(app, auth_service)
    UserBlueprint(app, cognito_service)
    DataBlueprint(app, data_service)

    # Render Blueprints
    RenderBlueprint(app, url_prefix="")

    return app


if __name__ == "__main__":
    app = _create_app()
    app.run(host="0.0.0.0", port=5000)
