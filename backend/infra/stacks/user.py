from constructs import Construct
from aws_cdk import Stack
from constructs.cognito import CognitoConstruct

class UserStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, project_name: str, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.cognito_construct = CognitoConstruct(self, f"{project_name}-cognito-construct", rds, project_name, env, **kwargs)