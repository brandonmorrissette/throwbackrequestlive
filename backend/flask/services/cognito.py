"""
This module provides a service for interacting with AWS Cognito.
It includes functionalities to read, write, add, update, and delete users in Cognito.
"""

import json
import secrets
import string
from datetime import datetime
from typing import Any, Dict, List

import boto3
import redis

from backend.flask.config import Config
from backend.flask.exceptions.boto import raise_http_exception


def cognito_json_encoder(obj: Any) -> str:
    """
    JSON encoder function for Cognito objects.

    Args:
        obj: The object to encode.

    Returns:
        str: The JSON-encoded string.

    Raises:
        TypeError: If the object type is not serializable.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CognitoService:
    """
    Service for interacting with AWS Cognito.
    """

    @raise_http_exception
    def __init__(self, redis_client: redis.Redis, config: Config) -> None:
        """
        Initialize the CognitoService.

        Args:
            config (Config): The configuration object.
        """
        ssm_client = boto3.client("ssm", region_name=config.AWS_DEFAULT_REGION)

        self._user_pool_id = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/user-pool-id",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._cognito_client = boto3.client(
            "cognito-idp", region_name=config.AWS_DEFAULT_REGION
        )

        self._redis_client = redis_client

    @raise_http_exception
    def read_rows(self) -> List[Dict[str, Any]]:
        """
        Read users from Cognito.

        Returns:
            list: A list of users.
        """
        users = []
        response = self._cognito_client.list_users(UserPoolId=self._user_pool_id)
        for user in response["Users"]:
            username = user["Username"]

            # Move to group service
            groups_response = self._cognito_client.admin_list_groups_for_user(
                UserPoolId=self._user_pool_id, Username=username
            )
            groups = [group["GroupName"] for group in groups_response["Groups"]]
            user["Groups"] = groups

            self._persist_user(username, user)

            users.append(user)

        return users

    @raise_http_exception
    def write_rows(self, rows: List[Dict[str, Any]]) -> None:
        """
        Write users to Cognito.

        Args:
            rows (list): A list of user dictionaries.
        """
        existing_usernames = set(self._redis_client.keys())
        row_usernames = {row["Username"] for row in rows if "Username" in row}

        users_to_delete = existing_usernames - row_usernames
        for username in users_to_delete:
            self._delete_user(username)

        users_to_add = [
            row
            for row in rows
            if "Username" not in row or row["Username"] not in existing_usernames
        ]
        for user in users_to_add:
            self._add_user(user)

        row_dict = {row.get("Username"): row for row in rows if row.get("Username")}
        users_to_update = row_usernames & existing_usernames
        for username in users_to_update:
            self._update_user(username, row_dict[username])

    def _generate_temp_password(self) -> str:
        """
        Generate a temporary password.

        Returns:
            str: A temporary password.
        """
        characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(characters) for _ in range(12))

    @raise_http_exception
    def _add_user(self, user: Dict[str, Any]) -> None:
        """
        Add a user to Cognito.

        Args:
            user (dict): A user dictionary.
        """
        response = self._cognito_client.admin_create_user(
            Username=user["Email"],
            UserPoolId=self._user_pool_id,
            UserAttributes=[
                {"Name": "email", "Value": user["Email"]},
            ],
            TemporaryPassword=self._generate_temp_password(),
        )
        user = response["User"]
        self._persist_user(user["Username"], user)

    @raise_http_exception
    def _update_user(self, username: str, user: Dict[str, Any]) -> None:
        """
        Update a user in Cognito.

        Args:
            username (str): The username of the user.
            user (dict): A user dictionary.
        """
        self._cognito_client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": user["Email"]},
            ],
        )

        self._persist_user(username, user)

    @raise_http_exception
    def _delete_user(self, username: str) -> None:
        """
        Delete a user from Cognito.

        Args:
            username (str): The username of the user.
        """
        self._cognito_client.admin_delete_user(
            UserPoolId=self._user_pool_id,
            Username=username,
        )
        self._remove_user(username)

    def _persist_user(self, username: str, user: Dict[str, Any]) -> None:
        """
        Persist a user in Redis.

        Args:
            username (str): The username of the user.
            user (dict): A user dictionary.
        """
        self._redis_client.set(username, json.dumps(user, default=cognito_json_encoder))

    def _remove_user(self, username: str) -> None:
        """
        Remove a user from Redis.

        Args:
            username (str): The username of the user.
        """
        self._redis_client.delete(username)
