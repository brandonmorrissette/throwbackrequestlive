from constructs import Construct
from aws_cdk import Stack
from constructs.cognito import CognitoConstruct

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, project_name: str, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CognitoConstruct(self, f"{project_name}-CognitoConstruct", rds, env, **kwargs)