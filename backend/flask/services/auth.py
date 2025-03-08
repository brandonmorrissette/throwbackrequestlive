"""
This module provides the AuthService class for handling authentication.
"""

from datetime import datetime, timedelta, timezone

import boto3
import jwt

from backend.flask.config import Config
from backend.flask.exceptions.boto import raise_http_exception


class AuthService:
    """
    Service for handling authentication.
    """

    @raise_http_exception
    def __init__(self, config: Config) -> None:
        """
        Initialize the AuthService.

        Args:
            config (Config): The configuration object.
        """
        self._client = boto3.client("cognito-idp", region_name=config.cognito_region)
        self._client_id = config.cognito_app_client_id
        self._user_pool_id = config.cognito_user_pool_id
        self._jwt_secret_key = config.jwt_secret_key
        self._jwt_algorithm = "HS256"

    @raise_http_exception
    def authenticate_user(self, username: str, password: str) -> dict:
        """
        Authenticate a user.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            dict: A dictionary containing the JWT token and any errors.
        """
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
    def reset_password(self, username: str, password: str, session: str) -> dict:
        """
        Reset a user's password.

        Args:
            username (str): The username of the user.
            password (str): The new password of the user.
            session (str): The session token.

        Returns:
            dict: A dictionary containing the JWT token.
        """
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
    def get_groups_by_username(self, username: str) -> list:
        """
        Get the groups a user belongs to.

        Args:
            username (str): The username of the user.

        Returns:
            list: A list of group names.
        """
        response = self._client.admin_list_groups_for_user(
            UserPoolId=self._user_pool_id, Username=username
        )
        groups = [group["GroupName"] for group in response.get("Groups", [])]
        return groups

    def generate_jwt(self, username: str, groups: list) -> str:
        """
        Generate a JWT token.

        Args:
            username (str): The username of the user.
            groups (list): A list of group names.

        Returns:
            str: The JWT token.
        """
        payload = {
            "sub": username,
            "username": username,
            "groups": groups,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }

        token = jwt.encode(payload, self._jwt_secret_key, algorithm=self._jwt_algorithm)
        return token
