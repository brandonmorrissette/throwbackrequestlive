"""
This module defines the RuntimeStack class,
which sets up the runtime environment for the application.

It creates ECS runtime constructs and Route 53 configurations
using the provided AWS resources and configuration.
"""

from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import aws_iam as iam
from aws_cdk import aws_route53 as route53
from constructs import Construct

from infra.config import Config
from infra.constructs.route_53 import Route53Construct, Route53ConstructArgs
from infra.constructs.runtime import RuntimeConstruct, RuntimeConstructArgs
from infra.stacks.stack import Stack, StackArgs


class RuntimeStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the RuntimeStack class.

    Attributes:
        config (Config): Configuration object.
        certificate (acm.ICertificate): The ACM certificate for the load balancer.
        hosted_zone (route53.IHostedZone): The Route 53 hosted zone.
        policy (iam.ManagedPolicy): The IAM managed policy for the task role.
        cluster (ecs.Cluster): The ECS cluster.
        db_credentials_arn (str): The ARN of the database credentials secret.
        cache_cluster (elasticache.CfnCacheCluster): The cache cluster.
        uid (str): The ID of the stack.
            Defaults to "runtime".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        certificate: acm.ICertificate,
        hosted_zone: route53.IHostedZone,
        policy: iam.ManagedPolicy,
        cluster: ecs.Cluster,
        db_credentials_arn: str,
        cache_cluster: elasticache.CfnCacheCluster,
        uid: str = "runtime",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.certificate = certificate
        self.hosted_zone = hosted_zone
        self.policy = policy
        self.cluster = cluster
        self.db_credentials_arn = db_credentials_arn
        self.cache_cluster = cache_cluster


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
                certificate=args.certificate,
                policy=args.policy,
                cluster=args.cluster,
                db_credentials_arn=args.db_credentials_arn,
                runtime_variables={
                    # pylint:disable=line-too-long
                    "PROJECT_NAME": str(args.config.project_name),
                    "ENVIRONMENT": str(args.config.environment_name),
                    "REDIS_HOST": str(args.cache_cluster.attr_redis_endpoint_address),
                    "REDIS_PORT": str(args.cache_cluster.attr_redis_endpoint_port),
                },
            ),
        )

        Route53Construct(
            self,
            Route53ConstructArgs(
                args.config,
                hosted_zone=args.hosted_zone,
                load_balancer=runtime_construct.runtime_service.load_balancer,
            ),
        )
