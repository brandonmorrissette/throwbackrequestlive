from flask import Flask
from flask_jwt_extended import JWTManager
import os
import boto3
import logging

def create_app():
    app = Flask(
            __name__, 
            template_folder='webapp/templates', static_folder='webapp/static'
        )

    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.DEBUG)

    app.config['COGNITO_REGION'] = os.getenv('AWS_REGION', 'us-east-1')  
    app.config['COGNITO_USER_POOL_ID'] = os.getenv('COGNITO_USER_POOL_ID')
    app.config['COGNITO_APP_CLIENT_ID'] = os.getenv('COGNITO_APP_CLIENT_ID')

    jwt = JWTManager(app)  

    cognito = boto3.client('cognito-idp', region_name=app.config['COGNITO_REGION'])

    with app.app_context():
        from webapp import routes
        app.register_blueprint(routes.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
