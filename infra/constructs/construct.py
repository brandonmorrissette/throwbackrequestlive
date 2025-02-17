from config import Config
from constructs import Construct as AwsCdKConstruct
from resources.resource import Resource


class Construct(AwsCdKConstruct, Resource):
    def __init__(
        self,
        scope: AwsCdKConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        Resource.__init__(self, scope, config, id, suffix)
        super().__init__(self.scope, self.id)
