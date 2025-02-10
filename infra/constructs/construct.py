from config import Config
from constructs import IConstruct
from resources.resource import Resource


class Construct(IConstruct, Resource):
    def __init__(
        self,
        scope: IConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        Resource.__init__(self, scope, config, id, suffix)
        super().__init__(scope, id, environment=config.cdk_environment)
