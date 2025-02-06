from config import Config
from constructs import IConstruct as AwsCdKIConstruct
from constructs import Stacj as AwsCdkStack


class Stack(AwsCdkStack, AwsCdKIConstruct):
    def __init__(self, scope, config: Config, suffix=None, **kwargs):
        AwsCdKIConstruct.__init__(self, scope, config, suffix)
        super().__init__(self.scope, self.id, env=config.cdk_environment, **kwargs)
