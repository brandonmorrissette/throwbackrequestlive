from constructs import Construct
from stacks.stack import Stack
from constructs.cognito import CognitoConstruct

class SetupStack(Stack):

    def __init__(self, scope: Construct, id: str, rds, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        env = kwargs.get('env')
        project_name = env.project_name if env else "default_project_name"

        CognitoConstruct(self, f"{project_name}-CognitoConstruct", rds)