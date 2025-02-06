from config import Config
from constructs import Construct as AwsCdKConstruct
from constructs import IConstruct as AwsCdKIConstruct


class Construct(AwsCdKConstruct, AwsCdKIConstruct):
    def __init__(
        self, scope: AwsCdKConstruct, config: Config, suffix=None, **kwargs
    ) -> None:
        AwsCdKIConstruct.__init__(self, scope, config, suffix)
        super().__init__(self.scope, self.id, env=config.cdk_environment, **kwargs)


class IConstruct(AwsCdKIConstruct):
    def __init__(self, scope: AwsCdKIConstruct, config: Config, suffix=None) -> None:
        self.scope = scope
        self.id = f"{config.project_name}-{config.environment_name}"

        if suffix:
            self.id = f"{self.id}-{suffix}"
