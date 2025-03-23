# pylint: disable=too-few-public-methods
"""
This module provides the Resource class for standardizing default IDs for cloud resources.
"""
from infra.config import Config


class ResourceArgs:
    """
    Arguments for the Resource class.

    Attributes:
        config (Config): Configuration object.
        uid (str, optional): The identifier for the resource.
            Defaults to None.
        prefix (str, optional): The prefix to prepend to the ID.
            Defaults to None.
    """

    def __init__(self, config: Config, uid: str = "", prefix: str = "") -> None:
        self.config = config
        self.uid = uid
        self.prefix = prefix


class Resource:
    """
    A class to standardize default IDs for cloud resources.

    Attributes:
        id (str): The identifier for the resource.
    """

    def format_id(
        self,
        args: ResourceArgs,
    ) -> str:
        """
        Formats the ID for a cloud resource.

        Args:
            args (ResourceArgs): The arguments containing config, uid, and prefix.

        Returns:
            str: The formatted ID.
        """
        formatted = (
            args.prefix
            if args.prefix
            else f"{args.config.project_name}-{args.config.environment_name}"
        )

        if args.uid:
            formatted = f"{formatted}-{args.uid}"
        return formatted
