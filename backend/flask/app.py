import os

from flask import Flask
from routes.auth import auth_bp
from routes.data import data_bp
from routes.render import render_bp
from routes.superuser import superuser_bp


def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(superuser_bp, url_prefix="/api/superuser")
    app.register_blueprint(data_bp, url_prefix="/api/data")
    app.register_blueprint(render_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
