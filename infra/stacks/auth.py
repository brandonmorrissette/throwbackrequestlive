
from aws_cdk import core
from constructs import Construct
from infra.constructs.cognito import CognitoConstruct

class AuthStack(core.Stack):
    def __init__(self, scope: Construct, id: str, superuser_email: str, rds, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CognitoConstruct(self, "CognitoConstruct", superuser_email=superuser_email, rds=rds)