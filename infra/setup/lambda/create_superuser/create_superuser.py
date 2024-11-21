import boto3
import os

def handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = os.environ['USER_POOL_ID']
    superuser_email = event['email'] 
    
    try:
        client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=superuser_email
        )
        print(f"User {superuser_email} already exists.")
    except client.exceptions.UserNotFoundException:
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
    
    return {
        'statusCode': 200,
        'body': 'Superuser setup completed.'
    }