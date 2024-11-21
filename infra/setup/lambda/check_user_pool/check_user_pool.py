
import boto3
import os

def handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_name = os.environ['USER_POOL_NAME']
    
    response = client.list_user_pools(MaxResults=60)
    user_pools = response['UserPools']
    
    exists = any(up['Name'] == user_pool_name for up in user_pools)
    
    return {
        'Exists': 'true' if exists else 'false'
    }