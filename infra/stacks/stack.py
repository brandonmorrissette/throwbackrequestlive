from aws_cdk import Stack as AwsCdkStack
from config import Config


class Stack(AwsCdkStack):
    def __init__(self, scope, config: Config, suffix=None, **kwargs):
        id = f"{config.project_name}-{config.environment_name}"
        if suffix:
            id = f"{id}-{suffix}"

        super().__init__(scope, id, env=config.cdk_environment, **kwargs)
