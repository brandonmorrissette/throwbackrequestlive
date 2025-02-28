from config import Config
from constructs import Construct as AwsCdkConstruct
from resources.resource import Resource


class Construct(AwsCdkConstruct, Resource):
    def __init__(
        self,
        scope: AwsCdkConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        Resource.__init__(self, config, id, suffix)
        super().__init__(scope, self.id)
