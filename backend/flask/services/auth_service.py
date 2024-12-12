import logging
from datetime import datetime, timedelta

import boto3
import jwt
from botocore.exceptions import ClientError


class AuthService:
    def __init__(self, config):
        self._client = boto3.client(
            "cognito-idp", region_name=config["cognito"]["COGNITO_REGION"]
        )
        self._client_id = config["cognito"]["COGNITO_APP_CLIENT_ID"]
        self._user_pool_id = config["cognito"]["COGNITO_USER_POOL_ID"]
        self._jwt_secret = config["jwt"]["JWT_SECRET_KEY"]
        logging.info(f"JWT_SECRET_KEY : {self._jwt_secret}")
        self._jwt_algorithm = "HS256"

    def authenticate_user(self, username, password):
        try:
            response = self._client.initiate_auth(
                ClientId=self._client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
            if response.get("ChallengeName") == "NEW_PASSWORD_REQUIRED":
                return {
                    "token": self.generate_jwt(
                        username, self.get_groups_by_username(username)
                    ),
                    "error": "NEW_PASSWORD_REQUIRED",
                    "session": response.get("Session"),
                }

            return {
                "token": self.generate_jwt(
                    username, self.get_groups_by_username(username)
                )
            }

        except ClientError as e:
            raise Exception(f"Authentication failed: {e.response['Error']['Message']}")

    def reset_password(self, username, password, session):
        try:
            response = self._client.respond_to_auth_challenge(
                ClientId=self._client_id,
                ChallengeName="NEW_PASSWORD_REQUIRED",
                ChallengeResponses={"USERNAME": username, "NEW_PASSWORD": password},
                Session=session,
            )

            return {
                "token": self.generate_jwt(
                    username, self.get_groups_by_username(username)
                )
            }

        except ClientError as e:
            raise Exception(f"Password reset failed: {e.response['Error']['Message']}")

    def get_groups_by_username(self, username):
        try:
            response = self._client.admin_list_groups_for_user(
                UserPoolId=self._user_pool_id, Username=username
            )
            groups = [group["GroupName"] for group in response.get("Groups", [])]
            return groups
        except ClientError as e:
            logging.error(f"Error fetching user groups: {e}")
            return []

    def generate_jwt(self, username, groups):
        payload = {
            "sub": username,
            "username": username,
            "groups": groups,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)
        return token
