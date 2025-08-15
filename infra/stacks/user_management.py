"""
This module defines the UserManagementStack class,
which sets up the user management resources for the application.

It creates User Pool and Superuser constructs using the provided configuration.
"""

from constructs import Construct

from infra.config import Config
from infra.constructs.superuser import SuperUserConstruct, SuperUserConstructArgs
from infra.constructs.userpool import UserPoolConstruct, UserPoolConstructArgs
from infra.stacks.stack import Stack, StackArgs


class UserManagementStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the UserManagementStack.

    Attributes:
        config (Config): Configuration object.
        uid (str): The ID of the stack.
            Defaults to "user-management".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        uid: str = "user-management",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


class UserManagementStack(Stack):
    """
    This stack sets up the user management resources for the application.

    It creates User Pool and Superuser constructs using the provided configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: UserManagementStackArgs,
    ) -> None:
        """
        Initialize the UserManagementStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (UserManagementStackArgs): The arguments for the stack.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.user_pool_construct = UserPoolConstruct(
            self, UserPoolConstructArgs(args.config)
        )
        self.superuser_construct = SuperUserConstruct(
            self,
            SuperUserConstructArgs(args.config, self.user_pool_construct.user_pool_id),
        )
