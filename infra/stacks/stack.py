import aws_cdk as cdk
from aws_cdk import Stack as CdkStack
from constructs import Construct

class Stack(CdkStack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        env = kwargs.get('env')
        super().__init__(scope, id, **kwargs)
        if env:
            self.add_env_tags(env)

    def add_env_tags(self, env):
        for key, value in vars(env).items():
            if isinstance(value, str):
                cdk.Tags.of(self).add(key, value)