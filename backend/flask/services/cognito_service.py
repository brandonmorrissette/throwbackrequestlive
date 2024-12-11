import secrets
import string

import boto3


class CognitoService:
    def __init__(self, config):
        self._user_pool_id = config["cognito"]["COGNITO_USER_POOL_ID"]
        self._client = boto3.client(
            "cognito-idp", region_name=config["cognito"]["COGNITO_REGION"]
        )

    def generate_temp_password(self):
        characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(characters) for _ in range(12))

    def add_user(self, email, username, groups):
        self._client.admin_create_user(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
            TemporaryPassword=self.generate_temp_password(),
        )
        for group in groups:
            self._client.admin_add_user_to_group(
                UserPoolId=self._user_pool_id,
                Username=username,
                GroupName=group,
            )

    def update_user(self, username, email, groups):
        self._client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        existing_groups = self._client.admin_list_groups_for_user(
            UserPoolId=self._user_pool_id,
            Username=username,
        )["Groups"]
        for group in existing_groups:
            self._client.admin_remove_user_from_group(
                UserPoolId=self._user_pool_id,
                Username=username,
                GroupName=group["GroupName"],
            )
        for group in groups:
            self._client.admin_add_user_to_group(
                UserPoolId=self._user_pool_id,
                Username=username,
                GroupName=group,
            )

    def delete_user(self, username):
        self._client.admin_delete_user(
            UserPoolId=self._user_pool_id,
            Username=username,
        )

    def list_groups(self):
        response = self._client.list_groups(UserPoolId=self._user_pool_id)
        return [group["GroupName"] for group in response["Groups"]]

    def list_users(self):
        response = self._client.list_users(UserPoolId=self._user_pool_id)
        return [
            {
                "username": user["Username"],
                "email": next(
                    (
                        attr["Value"]
                        for attr in user["Attributes"]
                        if attr["Name"] == "email"
                    ),
                    None,
                ),
                "groups": [
                    group["GroupName"]
                    for group in self._client.admin_list_groups_for_user(
                        Username=user["Username"], UserPoolId=self._user_pool_id
                    )["Groups"]
                ],
            }
            for user in response["Users"]
        ]
