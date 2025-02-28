from aws_cdk import Stack as AwsCdkStack
from config import Config
from constructs import Construct as AwsCdkConstruct
from resources.resource import Resource


class Stack(AwsCdkStack, Resource):
    def __init__(
        self,
        scope: AwsCdkConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
        **kwargs
    ):
        Resource.__init__(self, config, id, suffix)
        super().__init__(scope, self.id, env=config.cdk_environment, **kwargs)
