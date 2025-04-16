"""
This module provides the AuthService class for handling authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

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
        self._cognito_client = boto3.client(
            "cognito-idp", region_name=config.AWS_DEFAULT_REGION
        )

        ssm_client = boto3.client("ssm", region_name=config.AWS_DEFAULT_REGION)

        self._client_id: str = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/user-pool-client-id",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._user_pool_id: str = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/user-pool-id",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._jwt_secret_key: str = config.JWT_SECRET_KEY
        self._jwt_algorithm: str = "HS256"

    @raise_http_exception
    def authenticate_user(
        self, username: str, password: str
    ) -> Dict[str, Optional[str]]:
        """
        Authenticate a user.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            dict: A dictionary containing the JWT token and any errors.
        """
        response: dict = self._cognito_client.initiate_auth(
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
    def reset_password(
        self, username: str, password: str, session: str
    ) -> Dict[str, str]:
        """
        Reset a user's password.

        Args:
            username (str): The username of the user.
            password (str): The new password of the user.
            session (str): The session token.

        Returns:
            dict: A dictionary containing the JWT token.
        """
        self._cognito_client.respond_to_auth_challenge(
            ClientId=self._client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={"USERNAME": username, "NEW_PASSWORD": password},
            Session=session,
        )

        return {
            "token": self.generate_jwt(username, self.get_groups_by_username(username))
        }

    @raise_http_exception
    def get_groups_by_username(self, username: str) -> List[str]:
        """
        Get the groups a user belongs to.

        Args:
            username (str): The username of the user.

        Returns:
            list: A list of group names.
        """
        response: dict = self._cognito_client.admin_list_groups_for_user(
            UserPoolId=self._user_pool_id, Username=username
        )
        groups: List[str] = [group["GroupName"] for group in response.get("Groups", [])]
        return groups

    def generate_jwt(self, username: str, groups: List[str]) -> str:
        """
        Generate a JWT token.

        Args:
            username (str): The username of the user.
            groups (list): A list of group names.

        Returns:
            str: The JWT token.
        """
        payload: dict = {
            "sub": username,
            "username": username,
            "groups": groups,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }

        token: str = jwt.encode(
            payload, self._jwt_secret_key, algorithm=self._jwt_algorithm
        )
        return token
