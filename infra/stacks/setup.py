from aws_cdk import (
    aws_lambda as _lambda
)
from constructs import Construct
from stacks.stack import Stack

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, superuser_email: str, user_pool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        create_superuser_lambda = _lambda.Function(
            self, 'CreateSuperuserLambda',
            runtime=_lambda.Runtime.NODEJS_14_X,
            handler='create-superuser-lambda.handler',
            code=_lambda.Code.from_asset('infra/setup/lambda'),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'SUPERUSER_EMAIL': superuser_email
            }
        )