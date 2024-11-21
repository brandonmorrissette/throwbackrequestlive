from .stack import Stack
from constructs import Construct
from constructs.cognito import CognitoConstruct

class AuthStack(Stack):
    def __init__(self, scope: Construct, id: str, superuser_email: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CognitoConstruct(self, "CognitoConstruct", superuser_email=superuser_email, rds=rds, project_name=project_name)