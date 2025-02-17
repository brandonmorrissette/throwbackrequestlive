import json
import secrets
import string
from datetime import datetime

import boto3
import redis
from config import Config
from exceptions.boto import raise_http_exception


def cognito_json_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CognitoService:
    @raise_http_exception
    def __init__(self, config: Config):
        self._user_pool_id = config.COGNITO_USER_POOL_ID
        self._cognito_client = boto3.client(
            "cognito-idp", region_name=config.COGNITO_REGION
        )

        self.redis_client = redis.StrictRedis(
            host=config.REDIS_HOST,
            port=int(config.REDIS_PORT),
            decode_responses=True,
        )

    @raise_http_exception
    def read_rows(self):
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

            self.redis_client.set(
                username, json.dumps(user, default=cognito_json_encoder)
            )

            users.append(user)

        return users

    @raise_http_exception
    def write_rows(self, rows):
        existing_usernames = {key for key in self.redis_client.keys()}
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

    def _generate_temp_password(self):
        characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(characters) for _ in range(12))

    @raise_http_exception
    def _add_user(self, user):
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
    def _update_user(self, username, user):
        self._cognito_client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": user["Email"]},
            ],
        )

        self._persist_user(username, user)

    @raise_http_exception
    def _delete_user(self, username):
        self._cognito_client.admin_delete_user(
            UserPoolId=self._user_pool_id,
            Username=username,
        )
        self._remove_user(username)

    def _persist_user(self, username, user):
        self.redis_client.set(username, json.dumps(user, default=cognito_json_encoder))

    def _remove_user(self, username):
        self.redis_client.delete(username)
