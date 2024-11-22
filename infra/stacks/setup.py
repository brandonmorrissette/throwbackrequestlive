from constructs import Construct
from stacks.stack import Stack
from constructs.cognito import CognitoConstruct

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CognitoConstruct(self, f"{project_name}-CognitoConstruct", rds, project_name=project_name, **kwargs)