"""
This module defines the RuntimeStack class,
which sets up the runtime environment for the application.

It creates ECS runtime constructs and Route 53 configurations
using the provided stacks and configuration.
"""

from constructs import Construct

from infra.config import Config
from infra.constructs.route_53 import Route53Construct, Route53ConstructArgs
from infra.constructs.runtime import RuntimeConstruct, RuntimeConstructArgs
from infra.stacks.compute import ComputeStack
from infra.stacks.network import NetworkStack
from infra.stacks.stack import Stack, StackArgs
from infra.stacks.storage import StorageStack
from infra.stacks.user_management import UserManagementStack


class RuntimeStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the RuntimeStack class.

    Attributes:
        config (Config): Configuration object.
        user_management_stack (UserManagementStack): The user management stack.
        network_stack (NetworkStack): The network stack.
        compute_stack (ComputeStack): The compute stack.
        storage_stack (StorageStack): The storage stack.
        uid (str): The ID of the stack.
            Defaults to "runtime".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        user_management_stack: UserManagementStack,
        network_stack: NetworkStack,
        compute_stack: ComputeStack,
        storage_stack: StorageStack,
        uid: str = "runtime",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.user_management_stack = user_management_stack
        self.network_stack = network_stack
        self.compute_stack = compute_stack
        self.storage_stack = storage_stack


class RuntimeStack(Stack):
    """
    This stack sets up the runtime environment for the application.

    It creates ECS runtime constructs and Route 53 configurations
    using the provided stacks and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: RuntimeStackArgs,
    ) -> None:
        """
        Initialize the RuntimeStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (RuntimeStackArgs): The arguments for the stack.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        runtime_construct = RuntimeConstruct(
            self,
            RuntimeConstructArgs(
                config=args.config,
                certificate=args.network_stack.cert_construct.certificate,
                policy=args.user_management_stack.superuser_construct.policy,
                cluster=args.compute_stack.cluster_construct.cluster,
                db_credentials_arn=args.storage_stack.rds_construct.db_instance.secret.secret_arn,
                runtime_variables={
                    # pylint:disable=line-too-long
                    "PROJECT_NAME": args.config.project_name,
                    "ENVIRONMENT": args.config.environment_name,
                    "REDIS_HOST": args.storage_stack.cache_construct.cluster.attr_redis_endpoint_address,
                    "REDIS_PORT": args.storage_stack.cache_construct.cluster.attr_redis_endpoint_port,
                },
            ),
        )

        Route53Construct(
            self,
            Route53ConstructArgs(
                args.config,
                hosted_zone=args.network_stack.cert_construct.hosted_zone,
                load_balancer=runtime_construct.runtime_service.load_balancer,
            ),
        )
