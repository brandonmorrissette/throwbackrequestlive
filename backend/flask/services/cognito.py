import json
import secrets
import string
from datetime import datetime

import boto3
import redis


def cognito_json_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CognitoService:
    def __init__(self, config):
        self._user_pool_id = config["cognito"]["COGNITO_USER_POOL_ID"]
        self._client = boto3.client(
            "cognito-idp", region_name=config["cognito"]["COGNITO_REGION"]
        )

        redis_config = config.get("redis", {})
        self.redis_host = redis_config.get("REDIS_HOST", "redis")
        self.redis_port = redis_config.get("REDIS_PORT", 6379)

        self.redis_client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )

    def read_rows(self):
        response = self._client.list_users(UserPoolId=self._user_pool_id)
        users = []
        for user in response["Users"]:
            username = user["Username"]

            # Move to group service
            groups_response = self._client.admin_list_groups_for_user(
                UserPoolId=self._user_pool_id, Username=username
            )
            groups = [group["GroupName"] for group in groups_response["Groups"]]
            user["Groups"] = groups

            self.redis_client.set(
                username, json.dumps(user, default=cognito_json_encoder)
            )

            users.append(user)

        return users

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

    def _add_user(self, user):
        response = self._client.admin_create_user(
            Username=user["Email"],
            UserPoolId=self._user_pool_id,
            UserAttributes=[
                {"Name": "email", "Value": user["Email"]},
            ],
            TemporaryPassword=self._generate_temp_password(),
        )
        user = response["User"]
        self._persist_user(user["Username"], user)

    def _update_user(self, username, user):
        self._client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": user["Email"]},
            ],
        )

        self._persist_user(username, user)

    def _delete_user(self, username):
        self._client.admin_delete_user(
            UserPoolId=self._user_pool_id,
            Username=username,
        )
        self._remove_user(username)

    def _persist_user(self, username, user):
        self.redis_client.set(username, json.dumps(user, default=cognito_json_encoder))

    def _remove_user(self, username):
        self.redis_client.delete(username)
