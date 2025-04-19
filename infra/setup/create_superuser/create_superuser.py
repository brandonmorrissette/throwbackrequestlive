"""
This script creates a superuser in the Cognito user pool for the specified project.
It retrieves the project name and superuser email from environment variables,
checks if the user already exists, and if not, 
creates the user and adds them to the superuser group.
"""

import os

import boto3
import botocore

client = boto3.client("cognito-idp")

project_name = os.environ["PROJECT_NAME"]
superuser_email = os.environ["SUPERUSER_EMAIL"]
print(f" Project Name: {project_name}\n Superuser Email: {superuser_email}")
USERPOOLNAME = f"{project_name}-user-pool"

response = client.list_user_pools(MaxResults=60)
user_pool_id = None  # pylint: disable=invalid-name
for pool in response["UserPools"]:
    if pool["Name"] == USERPOOLNAME:
        user_pool_id = pool["Id"]
        break

if not user_pool_id:
    raise ValueError(f"User pool {USERPOOLNAME} not found.")

try:
    client.admin_get_user(UserPoolId=user_pool_id, Username=superuser_email)
    print(f"User {superuser_email} already exists.")
except client.exceptions.UserNotFoundException:
    try:
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=superuser_email,
            UserAttributes=[
                {"Name": "email", "Value": superuser_email},
            ],
        )
        print(f"User {superuser_email} created successfully.")
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=superuser_email,
            GroupName="superuser",
        )
        print(f"User {superuser_email} added to superuser groups.")
    except botocore.exceptions.ParamValidationError as e:
        print(f"Invalid parameters: {e}")
