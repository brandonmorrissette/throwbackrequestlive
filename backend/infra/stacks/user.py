from constructs import Construct
from aws_cdk import Stack, CfnOutput
from constructs.cognito import CognitoConstruct

class UserStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, project_name: str, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.cognito_construct = CognitoConstruct(self, f"{project_name}-cognito-construct", rds, project_name, env, **kwargs)
        CfnOutput(
            self, 
            f"{project_name}-user-pool-id",
            value=self.cognito_construct.user_pool.user_pool_id,
            export_name=f"{project_name}-user-pool-id"
        )