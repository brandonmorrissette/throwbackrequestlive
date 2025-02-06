from config import Config
from constructs import Construct as AwsCdKConstruct
from resources.resource import Resource


class Construct(AwsCdKConstruct, Resource):
    def __init__(
        self, scope: AwsCdKConstruct, config: Config, suffix=None, **kwargs
    ) -> None:
        Resource.__init__(self, scope, config, suffix)
        super().__init__(self.scope, self.id, env=config.cdk_environment, **kwargs)
