"""
This module contains the Stack class, which extends the AWS CDK Stack and Resource classes.

Classes:
    Stack: A stack that extends AWS CDK Stack and Resource classes.

Usage example:
    stack = Stack(scope, config)
"""

from aws_cdk import Stack as AwsCdkStack
from config import Config
from constructs import Construct as AwsCdkConstruct
from resources.resource import Resource


class Stack(AwsCdkStack, Resource):
    """
    A stack that extends AWS CDK Stack and Resource classes.

    Attributes:
        stack_id: The ID of the stack.
        suffix: The suffix for resource names.

    Methods:
        __init__: Initializes the Stack with the given parameters.
    """

    def __init__(
        self,
        scope: AwsCdkConstruct,
        config: Config,
        stack_id: str | None = None,
        suffix: str | None = None,
        **kwargs
    ):
        """
        Initializes the Stack with the given parameters.

        Args:
            scope (AwsCdkConstruct): The parent construct.
            config (Config): Configuration object.
            stack_id (str, optional): The ID of the stack.
                Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): Suffix for resource names. Defaults to None.
        """
        Resource.__init__(self, config, stack_id, suffix)
        super().__init__(scope, self.id, env=config.cdk_environment, **kwargs)
