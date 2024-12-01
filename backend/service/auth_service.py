import logging
import os
from datetime import datetime, timedelta

import boto3
import jwt
from botocore.exceptions import ClientError


class AuthService:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))
        self.client_id = os.getenv('COGNITO_APP_CLIENT_ID')
        self.jwt_secret = os.getenv('JWT_SECRET') 
        self.jwt_algorithm = "HS256" 
        
    def authenticate_user(self, username, password):
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': username, 'PASSWORD': password}
            )

            return {'token': self.generate_jwt(username, self.get_groups_by_username(username))}

        except ClientError as e:
            raise Exception(f"Authentication failed: {e.response['Error']['Message']}")

    def reset_password(self, username, password, session):
        try:
            response = self.client.respond_to_auth_challenge(
                ClientId=self.client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                ChallengeResponses={
                    'USERNAME': username,
                    'NEW_PASSWORD': password
                },
                Session=session
            )

            return {'token': self.generate_jwt(username, self.get_groups_by_username(username))}

        except ClientError as e:
            raise Exception(f"Password reset failed: {e.response['Error']['Message']}")

    def get_groups_by_username(self, username):
        try:
            response = self.client.admin_list_groups_for_user(
                UserPoolId=os.getenv('COGNITO_USER_POOL_ID'),
                Username=username
            )
            groups = [group['GroupName'] for group in response.get('Groups', [])]
            return groups
        except ClientError as e:
            logging.error(f"Error fetching user groups: {e}")
            return []

    def generate_jwt(self, username, groups):
        payload = {
            'sub': username,
            'username': username,
            'groups': groups,  
            'iat': datetime.utcnow(), 
            'exp': datetime.utcnow() + timedelta(hours=1) 
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
