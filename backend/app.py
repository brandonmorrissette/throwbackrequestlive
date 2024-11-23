from flask import Flask
from flask_jwt_extended import JWTManager
import os
import boto3
import logging

def create_app():
    app = Flask(
            __name__, 
            static_folder='../frontend/dist',
            static_url_path='/'
        )

    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        import api
        app.register_blueprint(api.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)