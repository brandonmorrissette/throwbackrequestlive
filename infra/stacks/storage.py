"""
This module defines the StorageStack class, which sets up the storage resources for the application.

It creates RDS and Cache constructs using the provided VPC and configuration.
"""

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct

from infra.config import Config
from infra.constructs.cache import CacheConstruct, CacheConstructArgs
from infra.constructs.rds import RdsConstruct, RdsConstructArgs
from infra.constructs.s3 import S3Construct
from infra.stacks.stack import Stack, StackArgs


class StorageStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the StorageStack class.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the storage resources.
        uid (str): The ID of the stack.
            Defaults to "storage".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        vpc: ec2.Vpc,
        uid: str = "storage",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc


class StorageStack(Stack):
    """
    This stack sets up the storage resources for the application.

    It creates RDS and Cache constructs using the provided VPC and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: StorageStackArgs,
    ) -> None:
        """
        Initialize the StorageStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (StorageStackArgs): Arguments containing the VPC and configuration.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.rds_construct = RdsConstruct(self, RdsConstructArgs(args.config, args.vpc))
        self.cache_construct = CacheConstruct(
            self, CacheConstructArgs(args.config, args.vpc)
        )
        self.s3_construct = S3Construct(
            self,
            args.config,
            load_balancer=args.load_balancer,
        )

        CfnOutput(
            self,
            "securitygroupid",
            value=self.rds_construct.security_group.security_group_id,
        )

        CfnOutput(
            self,
            "sqltaskdefinitionarn",
            value=self.rds_construct.task_definition.task_definition_arn,
        )
