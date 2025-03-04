"""
This module defines the UserManagementStack class, 
which sets up the user management resources for the application.

It creates User Pool and Superuser constructs using the provided configuration.
"""

from aws_cdk import CfnOutput
from config import Config
from constructs import Construct
from constructs.superuser import SuperUserConstruct
from constructs.userpool import UserPoolConstruct
from stacks.stack import Stack


class UserManagementStack(Stack):
    """
    This stack sets up the user management resources for the application.

    It creates User Pool and Superuser constructs using the provided configuration.
    """

    def __init__(
        self,
        scope: Construct,
        config: Config,
        stack_id: str | None = None,
    ) -> None:
        """
        Initialize the UserManagementStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            config (Config): The configuration object containing stack settings.
            stack_id (str, optional): The ID of the stack.
                Defaults to f"{config.project_name}-{config.environment_name}-user-management".
        """
        super().__init__(scope, config, stack_id, "user-management")

        self.user_pool_construct = UserPoolConstruct(self, config)
        self.superuser_construct = SuperUserConstruct(
            self, config, self.user_pool_construct.user_pool_id
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=self.superuser_construct.user_creation_task_def_arn,
        )
