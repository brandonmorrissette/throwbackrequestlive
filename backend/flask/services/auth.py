import logging
from datetime import datetime, timedelta

import boto3
import jwt
from botocore.exceptions import ClientError
from exceptions.http import HTTPException


class AuthException(HTTPException):
    """Custom exception to map a boto3 ClientError to an HTTPException"""

    def __init__(self, e: ClientError):

        message = e.response["Error"]["Message"]
        logging.error(f"Error authenticating user: {message}")

        super().__init__(description=message)
        self.code = e.response["ResponseMetadata"]["HTTPStatusCode"]


class AuthService:
    def __init__(self, config):
        self._client = boto3.client(
            "cognito-idp", region_name=config["cognito"]["COGNITO_REGION"]
        )
        self._client_id = config["cognito"]["COGNITO_APP_CLIENT_ID"]
        self._user_pool_id = config["cognito"]["COGNITO_USER_POOL_ID"]
        self._jwt_secret = config["jwt"]["JWT_SECRET_KEY"]
        self._jwt_algorithm = "HS256"

    def authenticate_user(self, username, password) -> dict:
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
            raise AuthException(e)

    def reset_password(self, username, password, session) -> dict:
        try:
            self._client.respond_to_auth_challenge(
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
            raise AuthException(e)

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
