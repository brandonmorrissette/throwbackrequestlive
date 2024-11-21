from aws_cdk import (
    aws_lambda as _lambda,
    custom_resources as cr,
    aws_logs as logs
)
from constructs import Construct
from stacks.stack import Stack
from constructs.cognito import CognitoConstruct

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, superuser_email: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        check_user_pool_lambda = _lambda.Function(
            self, 'CheckUserPoolLambda',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='check_user_pool.handler',
            code=_lambda.Code.from_asset('infra/setup/lambda/check_user_pool'),
            environment={
                'USER_POOL_NAME': f"{project_name}-UserPool"
            }
        )

        user_pool_exists_provider = cr.Provider(
            self, 'UserPoolExistsProvider',
            on_event_handler=check_user_pool_lambda,
            log_retention=logs.RetentionDays.ONE_DAY
        )

        user_pool_exists = cr.AwsCustomResource(
            self, 'UserPoolExists',
            service_token=user_pool_exists_provider.service_token
        )

        if not user_pool_exists.get_att('Exists').to_string() == 'true':
            cognito_construct = CognitoConstruct(self, "CognitoConstruct", rds=rds, project_name=project_name)

            create_superuser_lambda = _lambda.Function(
                self, 'CreateSuperuserLambda',
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler='create-superuser-lambda.handler',
                code=_lambda.Code.from_asset('infra/setup/lambda/create_superuser'),
                environment={
                    'USER_POOL_ID': cognito_construct.user_pool.user_pool_id,
                    'SUPERUSER_EMAIL': superuser_email
                }
            )

            create_superuser_lambda.node.add_dependency(cognito_construct.user_pool)