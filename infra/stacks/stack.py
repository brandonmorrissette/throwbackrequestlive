"""
This module contains the Stack class, which extends the AWS CDK Stack and Resource classes.

Classes:
    Stack: A stack that extends AWS CDK Stack and Resource classes.

Usage example:
    stack = Stack(scope, config)
"""

from aws_cdk import Stack as AwsCdkStack
from constructs import Construct as AwsCdkConstruct

from infra.resources.resource import Resource, ResourceArgs


class StackArgs(ResourceArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the Stack class.

    Attributes:
        config: Configuration object.
        uid (str): The ID of the stack.
            Defaults to None.
        prefix (str): Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}".
    """


class Stack(AwsCdkStack, Resource):
    """
    A stack that extends AWS CDK Stack and Resource classes.

    Attributes:
        stack_id: The ID of the stack.
        prefix: The prefix for resource names.

    Methods:
        __init__: Initializes the Stack with the given parameters.
    """

    def __init__(self, scope: AwsCdkConstruct, args: StackArgs, **kwargs):
        """
        Initializes the Stack with the given parameters.

        Args:
            scope (AwsCdkConstruct): The parent construct.
            args (StackArgs): The arguments for the stack.
        """
        super().__init__(
            scope, self.format_id(args), env=args.config.cdk_environment, **kwargs
        )
