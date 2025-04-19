"""
This module contains the ClusterConstruct class, which sets up an ECS cluster
within a specified VPC.

Classes:
    ClusterConstruct: A construct that sets up an ECS cluster.

Usage example:
    cluster_construct = ClusterConstruct(scope, config, vpc)
"""

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class ClusterConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the ClusterConstruct.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the ECS cluster.
        uid (str): The ID of the construct.
            Default is "cluster".
        prefix (str): The prefix for the construct ID.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self, config: Config, vpc: ec2.Vpc, uid: str = "cluster", prefix: str = ""
    ):
        super().__init__(config, uid, prefix)
        self.vpc = vpc


class ClusterConstruct(Construct):
    """
    A construct that sets up an ECS cluster.

    Attributes:
        cluster: The ECS cluster.

    Methods:
        __init__: Initializes the ClusterConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: ClusterConstructArgs,
    ) -> None:
        """
        Initializes the ClusterConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (ClusterConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        self.cluster = ecs.Cluster(
            self,
            f"{args.config.project_name}-{args.config.environment_name}-cluster",
            vpc=args.vpc,
        )
