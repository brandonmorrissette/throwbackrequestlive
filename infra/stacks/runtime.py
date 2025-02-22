from aws_cdk import aws_ecs as ecs
from config import Config
from constructs.construct import Construct
from constructs.route_53 import Route53Construct
from constructs.runtime_ecs import RuntimeEcsConstruct
from stacks.compute import ComputeStack
from stacks.network import NetworkStack
from stacks.stack import Stack
from stacks.storage import StorageStack
from stacks.user_management import UserManagementStack


class RuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        user_management_stack: UserManagementStack,
        network_stack: NetworkStack,
        compute_stack: ComputeStack,
        storage_stack: StorageStack,
        id: str | None = None,
        suffix: str | None = "runtime",
    ):
        super().__init__(scope, config, id, suffix)

        runtime_construct = RuntimeEcsConstruct(
            self,
            config,
            certificate=network_stack.cert_construct.certificate,
            policy=user_management_stack.superuser_construct.policy,
            cluster=compute_stack.cluster_construct.cluster,
            runtime_variables={
                "COGNITO_APP_CLIENT_ID": user_management_stack.user_pool_construct.app_client.ref,
                "COGNITO_USER_POOL_ID": user_management_stack.user_pool_construct.user_pool.user_pool_id,
                "DB_NAME": storage_stack.rds_construct.db_instance.database_name,
                "REDIS_HOST": storage_stack.cache_construct.cache_cluster.attr_redis_endpoint_address,
                "REDIS_PORT": storage_stack.cache_construct.cache_cluster.attr_redis_endpoint_port,
            },
            runtime_secrets={
                "DB_USER": storage_stack.rds_construct.db_instance.secret.secret_value_from_json(
                    "username"
                ),
                "DB_PASSWORD": storage_stack.rds_construct.db_instance.secret.secret_value_from_json(
                    "password"
                ),
                "DB_HOST": storage_stack.rds_construct.db_instance.db_instance_endpoint_address,
            },
        )

        Route53Construct(
            self,
            config,
            hosted_zone=network_stack.cert_construct.hosted_zone,
            load_balancer=runtime_construct.load_balancer,
        )
