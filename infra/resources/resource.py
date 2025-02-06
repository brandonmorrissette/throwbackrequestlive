from config import Config
from constructs import IConstruct


class Resource:
    def __init__(
        self,
        scope: IConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:

        self.scope = scope

        if not id:
            self.id = f"{config.project_name}-{config.environment_name}"

        if suffix:
            self.id = f"{self.id}-{suffix}"
