"""
This module provides the AuthService class for handling authentication.
"""

import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import boto3
import jwt
import redis
from flask import current_app as app
from sqlalchemy import select

from backend.flask.config import Config
from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.services.data import DataService


class AuthService(DataService):
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
        super().__init__(config)

        self._cognito_client = boto3.client(
            "cognito-idp", region_name=config.AWS_DEFAULT_REGION
        )

        ssm_client = boto3.client("ssm", region_name=config.AWS_DEFAULT_REGION)

        self._client_id = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/user-pool-client-id",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._user_pool_id = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/user-pool-id",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._jwt_secret_key = config.JWT_SECRET_KEY
        self._jwt_algorithm = "HS256"

        self._redis_client = redis.StrictRedis(
            host=config.redis_host,
            port=int(config.redis_port),
            decode_responses=True,
        )

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
        response = self._cognito_client.initiate_auth(
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
    def get_groups_by_username(self, username: str) -> list:
        """
        Get the groups a user belongs to.

        Args:
            username (str): The username of the user.

        Returns:
            list: A list of group names.
        """
        response = self._cognito_client.admin_list_groups_for_user(
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

    def generate_uid(self) -> str:
        """
        Generate a unique identifier (UID) for a user.
        Returns:
            str: The generated UID.
        """
        return str(uuid4())

    def generate_access_key(self) -> str:
        """
        Generate an access key.

        Returns:
            str: The generated access key.
        """
        access_key = secrets.token_urlsafe(32)
        self._redis_client.set(access_key, access_key)
        self._redis_client.expire(access_key, 600)
        return access_key

    def validate_access_key(self, access_key: str) -> bool:
        """
        Validate the access key.

        Args:
            access_key (str): The access key to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return self._redis_client.exists(access_key) > 0


class RequestAuthService(AuthService):
    """
    Service for handling request authentication.
    """

    def get_shows_by_entry_point_id(self, entry_point_id: str) -> list:
        """
        Get shows by entry point ID.

        Args:
            entry_point_id (str): The entry point ID.

        Returns:
            list: A list of shows.
        """

        shows = self.get_table("shows")
        entrypoints = self.get_table("entrypoints")
        statement = (
            select(shows)
            .join(entrypoints, shows.c.entry_point_id == entrypoints.c.id)
            .where(entrypoints.c.id == entry_point_id)
        )
        app.logger.debug(f"Statement: {statement}")
        return self.execute(statement)
