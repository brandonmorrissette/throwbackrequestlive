import logging
from datetime import datetime, timedelta

import boto3
import jwt
from config import Config
from exceptions.boto import raise_http_exception


class AuthService:
    @raise_http_exception
    def __init__(self, config: Config):
        self._client = boto3.client("cognito-idp", region_name=config.COGNITO_REGION)
        self._client_id = config.COGNITO_APP_CLIENT_ID
        self._user_pool_id = config.COGNITO_USER_POOL_ID
        self._jwt_secret = config.JWT_SECRET_KEY
        logging.info(f"JWT Secret Key: {self._jwt_secret}")
        self._jwt_algorithm = "HS256"

    @raise_http_exception
    def authenticate_user(self, username, password) -> dict:
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
            "token": self.generate_jwt(username, self.get_groups_by_username(username))
        }

    @raise_http_exception
    def reset_password(self, username, password, session) -> dict:
        self._client.respond_to_auth_challenge(
            ClientId=self._client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={"USERNAME": username, "NEW_PASSWORD": password},
            Session=session,
        )

        return {
            "token": self.generate_jwt(username, self.get_groups_by_username(username))
        }

    @raise_http_exception
    def get_groups_by_username(self, username) -> list:
        response = self._client.admin_list_groups_for_user(
            UserPoolId=self._user_pool_id, Username=username
        )
        groups = [group["GroupName"] for group in response.get("Groups", [])]
        return groups

    def generate_jwt(self, username, groups) -> str:
        payload = {
            "sub": username,
            "username": username,
            "groups": groups,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        logging.info(f"JWT Secret Key: {self._jwt_secret}")
        token = jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)
        return token
