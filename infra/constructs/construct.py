"""
This module contains the base Construct class, which sets default Resource attributes
to pass to the AWS CDK Construct.

Classes:
    Construct: A base construct that sets default Resource attributes.

Usage example:
    base_construct = Construct(scope, config)
"""

from config import Config
from constructs import Construct as AwsCdkConstruct
from resources.resource import Resource


class Construct(AwsCdkConstruct, Resource):
    """
    A base construct that sets default Resource attributes to pass to the AWS CDK Construct.

    Attributes:
        id: The ID of the construct.
        suffix: The suffix for resource names.

    Methods:
        __init__: Initializes the Construct with the given parameters.
    """

    def __init__(
        self,
        scope: AwsCdkConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        """
        Initializes the Construct with the given parameters.

        Args:
            scope (AwsCdkConstruct): The parent construct.
            config (Config): Configuration object.
            id (str, optional): The ID of the construct. Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): Suffix for resource names. Defaults to None.
        """
        Resource.__init__(self, config, id, suffix)
        super().__init__(scope, self.id)
