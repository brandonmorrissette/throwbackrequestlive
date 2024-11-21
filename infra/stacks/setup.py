import boto3
from aws_cdk import (
    aws_lambda as _lambda,
    custom_resources as cr,
    aws_logs as logs,
    aws_iam as iam
)
from constructs import Construct
from stacks.stack import Stack
from constructs.cognito import CognitoConstruct

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cognito_client = boto3.client('cognito-idp')

        user_pools = cognito_client.list_user_pools(MaxResults=60)
        user_pool_exists = any(pool['Name'] == f"{project_name}-UserPool" for pool in user_pools['UserPools'])

        user_pool_id = None
        for pool in user_pools['UserPools']:
            if pool['Name'] == f"{project_name}-UserPool":
                user_pool_id = pool['Id']
                break

        if not user_pool_exists:
            CognitoConstruct(self, "CognitoConstruct", rds=rds, project_name=project_name)

        create_superuser_lambda = _lambda.Function(
            self, 'CreateSuperuserLambda',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='create-superuser-lambda.handler',
            code=_lambda.Code.from_asset('infra/setup/lambda/create_superuser'),
            environment={
                'USER_POOL_ID': user_pool_id,
            }
        )