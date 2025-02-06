from aws_cdk import Stack as AwsCdkStack
from config import Config
from resources.resource import Resource


class Stack(AwsCdkStack, Resource):
    def __init__(
        self,
        scope,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
        **kwargs
    ):
        Resource.__init__(self, scope, config, id, suffix)
        super().__init__(self.scope, self.id, env=config.cdk_environment, **kwargs)
