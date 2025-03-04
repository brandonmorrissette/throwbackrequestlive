# pylint: disable=too-few-public-methods
"""
This module provides the Resource class for standardizing default IDs for cloud resources.
"""

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
        resource_id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        """
        Initialize a Resource instance.

        Args:
            config (Config): The configuration object containing project and environment names.
            id (str, optional): The initial ID for the resource.
                Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): An optional suffix to append to the ID. Defaults to None.
        """
        self.id = (
            resource_id
            if resource_id
            else f"{config.project_name}-{config.environment_name}"
        )

        if suffix:
            self.id = f"{self.id}-{suffix}"
