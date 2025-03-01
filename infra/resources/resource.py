from config import Config


class Resource:
    """
    A class to standardize default IDs for cloud resources.

    Attributes:
        id (str): The identifier for the resource.
    """

    def __init__(
        self,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        """
        Initialize a Resource instance.

        Args:
            config (Config): The configuration object containing project and environment names.
            id (str, optional): The initial ID for the resource. Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): An optional suffix to append to the ID. Defaults to None.
        """
        self.id = id if id else f"{config.project_name}-{config.environment_name}"

        suffix = suffix
        if suffix:
            self.id = f"{self.id}-{suffix}"
