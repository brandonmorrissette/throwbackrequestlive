import os

import boto3
import botocore

client = boto3.client("cognito-idp")

project_name = os.environ["PROJECT_NAME"]
superuser_email = os.environ["SUPERUSER_EMAIL"]
print(f" Project Name: {project_name}\n Superuser Email: {superuser_email}")

response = client.list_user_pools(MaxResults=60)
user_pool_id = None
for pool in response["UserPools"]:
    if pool["Name"] == f"{project_name}-user-pool":
        user_pool_id = pool["Id"]
        break

if not user_pool_id:
    raise Exception(f"User pool for project {project_name} not found.")

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
        print(f"User {superuser_email} added to admin and superuser groups.")
    except botocore.exceptions.ParamValidationError as e:
        print(f"Invalid parameters: {e}")
