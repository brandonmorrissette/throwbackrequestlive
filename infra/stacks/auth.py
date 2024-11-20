from constructs import Construct
from constructs.cognito import CognitoConstruct
from constructs.superuser import SuperuserConstruct
from .stack import Stack

class AuthStack(Stack):
    def __init__(self, scope: Construct, id: str, tags: dict, **kwargs):
        super().__init__(scope, id, tags, **kwargs)
        CognitoConstruct(self, "Cognito")
        SuperuserConstruct(self, "Superuser")

