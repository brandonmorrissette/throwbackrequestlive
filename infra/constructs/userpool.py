"""
This module contains the UserPoolConstruct class, which sets up a Cognito user pool
and client.

Classes:
    UserPoolConstruct: A construct that sets up a Cognito user pool and client.

Usage example:
    user_pool_construct = UserPoolConstruct(scope, config)
"""

import boto3
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ssm as ssm

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class UserPoolConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the UserPoolConstruct class.

    Attributes:
        config: Configuration object.
        uid: Unique identifier for the resource.
            Defaults to "user-pool".
        prefix: Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-user-pool".
    """

    def __init__(
        self,
        config: Config,
        uid: str = "user-pool",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


class UserPoolConstruct(Construct):
    """
    A construct that sets up a Cognito user pool and app client.

    Attributes:
        user_pool: The Cognito user pool.
        app_client: The Cognito app client.

    Methods:
        __init__: Initializes the UserPoolConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: UserPoolConstructArgs,
    ) -> None:
        """
        Initializes the UserPoolConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (UserPoolConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        self._cognito_client = boto3.client("cognito-idp")
        user_pool_name = (
            f"{args.config.project_name}-{args.config.environment_name}-user-pool"
        )

        user_pool = self._get_user_pool(user_pool_name)
        self.user_pool_id = user_pool.user_pool_id
        ssm.StringParameter(
            self,
            "UserPoolIdParameter",
            parameter_name=f"/{args.config.project_name}-{args.config.environment_name}"
            "/user-pool-id",
            string_value=user_pool.user_pool_id,
        )

        app_client = user_pool.add_client(
            "AppClient",
            user_pool_client_name=f"{user_pool_name}-app-client",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True,
            ),
        )
        ssm.StringParameter(
            self,
            "UserPoolClientIdParameter",
            parameter_name=f"/{args.config.project_name}-{args.config.environment_name}"
            "/user-pool-client-id",
            string_value=app_client.user_pool_client_id,
        )

    def _get_user_pool(self, user_pool_name):
        """
        Retrieves the Cognito user pool with the given name.
        If the user pool does not exist,
        it creates a new one.

        Args:
            user_pool_name (str): The name of the user pool.
            sleep_time (int, optional): The time to sleep between checks.
                Defaults to 5.
            max_checks (int, optional): The maximum number of checks.
                Defaults to 10.

        Returns:
            cognito.UserPool: The Cognito user pool.
        """
        for pool in self._cognito_client.list_user_pools(MaxResults=60).get(
            "UserPools", []
        ):
            if pool["Name"] == user_pool_name:
                return cognito.UserPool.from_user_pool_id(
                    self, user_pool_name, user_pool_id=pool["Id"]
                )

        return cognito.UserPool(
            self,
            f"{user_pool_name}",
            user_pool_name=user_pool_name,
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=False,
                require_uppercase=False,
                require_digits=False,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
        )
