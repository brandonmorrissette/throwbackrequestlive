import boto3
import os

client = boto3.client('cognito-idp')
user_pool_id = os.environ['USER_POOL_ID']
superuser_email = os.environ['SUPERUSER_EMAIL']

try:
    client.admin_get_user(
        UserPoolId=user_pool_id,
        Username=superuser_email
    )
    print(f'User {superuser_email} already exists.')
except client.exceptions.UserNotFoundException:
    try:
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=superuser_email,
            UserAttributes=[
                {'Name': 'email', 'Value': superuser_email},
            ],
        )
        print(f'User {superuser_email} created successfully.')
        # Add user to groups
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=superuser_email,
            GroupName='admin'
        )
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=superuser_email,
            GroupName='superuser'
        )
        print(f'User {superuser_email} added to admin and superuser groups.')
    except botocore.exceptions.ParamValidationError as e:
        print(f'Invalid parameters: {e}')