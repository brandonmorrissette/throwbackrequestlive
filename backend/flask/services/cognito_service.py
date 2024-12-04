import os
import secrets
import string

import boto3

USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


def generate_temp_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(characters) for _ in range(12))


def add_user(email, username, groups):
    cognito_client.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=username,
        UserAttributes=[{"Name": "email", "Value": email}],
        TemporaryPassword=generate_temp_password(),
    )
    for group in groups:
        cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=username,
            GroupName=group,
        )


def update_user(username, email, groups):
    cognito_client.admin_update_user_attributes(
        UserPoolId=USER_POOL_ID,
        Username=username,
        UserAttributes=[{"Name": "email", "Value": email}],
    )
    existing_groups = cognito_client.admin_list_groups_for_user(
        UserPoolId=USER_POOL_ID,
        Username=username,
    )["Groups"]
    for group in existing_groups:
        cognito_client.admin_remove_user_from_group(
            UserPoolId=USER_POOL_ID,
            Username=username,
            GroupName=group["GroupName"],
        )
    for group in groups:
        cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=username,
            GroupName=group,
        )


def delete_user(username):
    cognito_client.admin_delete_user(
        UserPoolId=USER_POOL_ID,
        Username=username,
    )


def list_groups():
    response = cognito_client.list_groups(UserPoolId=USER_POOL_ID)
    return [group["GroupName"] for group in response["Groups"]]


def list_users():
    response = cognito_client.list_users(UserPoolId=USER_POOL_ID)
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
                for group in cognito_client.admin_list_groups_for_user(
                    Username=user["Username"], UserPoolId=USER_POOL_ID
                )["Groups"]
            ],
        }
        for user in response["Users"]
    ]
