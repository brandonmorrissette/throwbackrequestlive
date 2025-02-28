from config import Config


class Resource:
    def __init__(
        self,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:

        self.id = id if id else f"{config.project_name}-{config.environment_name}"

        suffix = suffix
        if suffix:
            self.id = f"{self.id}-{suffix}"
