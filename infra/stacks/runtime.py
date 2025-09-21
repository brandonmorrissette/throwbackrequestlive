"""
This module defines the RuntimeStack class,
which sets up the runtime environment for the application.

It creates ECS runtime constructs and Route 53 configurations
using the provided AWS resources and configuration.
"""

from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3
from constructs import Construct

from infra.config import Config
from infra.constructs.runtime import RuntimeConstruct, RuntimeConstructArgs
from infra.stacks.stack import Stack, StackArgs


class RuntimeStackArgs(  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    StackArgs
):
    """
    A class that defines properties for the RuntimeStack class.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.IVpc): The VPC where the runtime constructs will be deployed.
        certificate (acm.ICertificate): The ACM certificate for the load balancer.
        policy (iam.ManagedPolicy): The IAM managed policy for the task role.
        cluster (ecs.Cluster): The ECS cluster.
        db_instance (rds.IDatabaseInstance): The database instance.
        gateway_security_group (ec2.ISecurityGroup): The security group for the API Gateway.
        uid (str): The ID of the stack.
            Defaults to "runtime".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        vpc: ec2.IVpc,
        certificate: acm.ICertificate,
        policy: iam.ManagedPolicy,
        cluster: ecs.Cluster,
        bucket: s3.IBucket,
        db_instance: rds.IDatabaseInstance,
        gateway_security_group: ec2.ISecurityGroup,
        uid: str = "runtime",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc
        self.certificate = certificate
        self.policy = policy
        self.cluster = cluster
        self.bucket = bucket
        self.db_instance = db_instance
        self.gateway_security_group = gateway_security_group


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

        RuntimeConstruct(
            self,
            RuntimeConstructArgs(
                config=args.config,
                vpc=args.vpc,
                certificate=args.certificate,
                policy=args.policy,
                cluster=args.cluster,
                bucket=args.bucket,
                db_instance=args.db_instance,
                gateway_security_group=args.gateway_security_group,
                runtime_variables={
                    # pylint:disable=line-too-long
                    "PROJECT_NAME": str(args.config.project_name),
                    "ENVIRONMENT": str(args.config.environment_name),
                },
            ),
        )
