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
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


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
        config: Config,
        vpc: ec2.Vpc,
        construct_id: str | None = None,
    ) -> None:
        """
        Initializes the ClusterConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            vpc (ec2.Vpc): The VPC in which to create the ECS cluster.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-cluster".
        """
        super().__init__(scope, config, construct_id, "cluster")

        self.cluster = ecs.Cluster(self, self.id, vpc=vpc)
