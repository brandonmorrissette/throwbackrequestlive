"""This module defines the ShowStack class for resources required ONLY during the show.

It creates the cache construct using the provided VPC and configuration
"""

from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infra.config import Config
from infra.constructs.cache import CacheConstruct, CacheConstructArgs
from infra.stacks.stack import Stack, StackArgs


class ShowStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines args for the ShowStack class.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the storage resources.
        uid (str): The ID of the stack.
            Defaults to "storage".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        vpc: ec2.Vpc,
        uid: str = "show",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc


class ShowStack(Stack):
    """
    This stack sets up the storage resources for the application.

    It creates RDS and Cache constructs using the provided VPC and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: ShowStackArgs,
    ) -> None:
        """
        Initialize the ShowStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (ShowStackArgs): Arguments containing the VPC and configuration.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.cache_construct = CacheConstruct(
            self, CacheConstructArgs(args.config, args.vpc)
        )
