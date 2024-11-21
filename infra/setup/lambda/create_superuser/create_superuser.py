import boto3
import os
import re
import botocore.exceptions

def handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = os.environ['USER_POOL_ID']
    superuser_email = event['email']
    
    print(f"Processing superuser email: {superuser_email}")
    
    try:
        client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=superuser_email
        )
        print(f"User {superuser_email} already exists.")
    except client.exceptions.UserNotFoundException:
        try:
            client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=superuser_email,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': superuser_email
                    },
                ],
            )
            print(f"User {superuser_email} created successfully.")
        except botocore.exceptions.ParamValidationError as e:
            return {
                'statusCode': 400,
                'body': f"Invalid parameters: {e}"
            }
    
    return {
        'statusCode': 200,
        'body': 'Superuser setup completed.'
    }