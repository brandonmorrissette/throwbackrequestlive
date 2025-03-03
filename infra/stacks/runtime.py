"""
This module defines the RuntimeStack class, 
which sets up the runtime environment for the application.

It creates ECS runtime constructs and Route 53 configurations 
using the provided stacks and configuration.
"""

from dataclasses import dataclass

from aws_cdk import aws_ecs as ecs
from config import Config
from constructs import Construct
from constructs.route_53 import Route53Construct, Route53ConstructArgs
from constructs.runtime_ecs import RuntimeEcsConstruct, RuntimeEcsConstructArgs
from stacks.compute import ComputeStack
from stacks.network import NetworkStack
from stacks.stack import Stack
from stacks.storage import StorageStack
from stacks.user_management import UserManagementStack


@dataclass
class RuntimeStackArgs:
    """
    A class that defines properties for the RuntimeStack class.

    Attributes:
        user_management_stack (UserManagementStack): The user management stack.
        network_stack (NetworkStack): The network stack.
        compute_stack (ComputeStack): The compute stack.
        storage_stack (StorageStack): The storage stack.
    """

    user_management_stack: UserManagementStack
    network_stack: NetworkStack
    compute_stack: ComputeStack
    storage_stack: StorageStack


class RuntimeStack(Stack):
    """
    This stack sets up the runtime environment for the application.

    It creates ECS runtime constructs and Route 53 configurations
    using the provided stacks and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        config: Config,
        args: RuntimeStackArgs,
        stack_id: str | None = None,
    ) -> None:
        """
        Initialize the RuntimeStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            config (Config): The configuration object containing stack settings.
            user_management_stack (UserManagementStack): The user management stack.
            network_stack (NetworkStack): The network stack.
            compute_stack (ComputeStack): The compute stack.
            storage_stack (StorageStack): The storage stack.
            stack_id (str, optional): The ID of the stack.
                Defaults to f"{config.project_name}-{config.environment_name}-runtime".
        """
        super().__init__(scope, config, stack_id, "runtime")

        runtime_construct = RuntimeEcsConstruct(
            self,
            config,
            RuntimeEcsConstructArgs(
                certificate=args.network_stack.cert_construct.certificate,
                policy=args.user_management_stack.superuser_construct.policy,
                cluster=args.compute_stack.cluster_construct.cluster,
                runtime_variables={
                    # pylint:disable=line-too-long
                    "COGNITO_APP_CLIENT_ID": args.user_management_stack.user_pool_construct.app_client.ref,
                    "COGNITO_USER_POOL_ID": args.user_management_stack.user_pool_construct.user_pool.user_pool_id,
                    # I'd like to update this to not use config.project_name, but have yet to find the right solution.
                    # The address requires a database name, which is not available in a db_instance
                    "DB_NAME": config.project_name,
                    "REDIS_HOST": args.storage_stack.cache_construct.cluster.attr_redis_endpoint_address,
                    "REDIS_PORT": args.storage_stack.cache_construct.cluster.attr_redis_endpoint_port,
                },
                runtime_secrets={
                    "DB_USER": ecs.Secret.from_secrets_manager(
                        args.storage_stack.rds_construct.db_instance.secret, "username"
                    ),
                    "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                        args.storage_stack.rds_construct.db_instance.secret, "password"
                    ),
                    "DB_HOST": ecs.Secret.from_secrets_manager(
                        args.storage_stack.rds_construct.db_instance.secret, "host"
                    ),
                },
            ),
        )

        Route53Construct(
            self,
            config,
            Route53ConstructArgs(
                hosted_zone=args.network_stack.cert_construct.hosted_zone,
                load_balancer=runtime_construct.runtime_service.load_balancer,
            ),
        )
