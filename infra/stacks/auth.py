from aws_cdk import Stack
from constructs import Construct
from constructs.cognito import CognitoConstruct
from constructs.superuser import SuperuserConstruct


class AuthStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        CognitoConstruct(self, "Cognito")
        SuperuserConstruct(self, "Superuser")
