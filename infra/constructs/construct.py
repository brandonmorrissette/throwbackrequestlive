"""
This module contains the Construct class which extends the AWS CDK Construct and Resource classes.

Classes:
    Construct: A base construct that sets default Resource attributes.

Usage example:
    base_construct = Construct(scope, config)
"""

from constructs import Construct as AwsConstruct

from infra.resources.resource import Resource, ResourceArgs


class ConstructArgs(ResourceArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the Construct class.

    Attributes:
        config: Configuration object.
        uid: Unique identifier for the resource.
            Defaults to None.
        prefix: Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-".
    """


class Construct(AwsConstruct, Resource):
    """
    A base construct that sets default Resource attributes to pass to the AWS CDK Construct.

    Attributes:
        construct_id: The ID of the construct.
            Defaults to None.
        prefix: The prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-".

    Methods:
        __init__: Initializes the Construct with the given parameters.
    """

    def __init__(
        self,
        scope: AwsConstruct,
        args: ConstructArgs,
    ) -> None:
        """
        Initializes the Construct with the given parameters.

        Args:
            scope (Construct): The parent construct.
            args (ConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, self.format_id(args))
