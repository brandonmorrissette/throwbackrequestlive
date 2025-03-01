"""
This module defines the ComputeStack class, which sets up the compute resources for the application.

It creates an ECS cluster using the provided VPC and configuration.
"""

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs import Construct
from constructs.cluster import ClusterConstruct
from stacks.stack import Stack


class ComputeStack(Stack):
    """
    This stack sets up the compute resources for the application.

    It creates an ECS cluster using the provided VPC and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc: ec2.Vpc,
        id: str | None = None,
        suffix: str | None = "compute",
    ) -> None:
        """
        Initialize the ComputeStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            config (Config): The configuration object containing stack settings.
            vpc (ec2.Vpc): The VPC in which to create the ECS cluster.
            id (str, optional): The ID of the stack. Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): The suffix to append to the stack name. Defaults to "compute".
        """
        super().__init__(scope, config, id, suffix)

        self.cluster_construct = ClusterConstruct(self, config, vpc=vpc)

        CfnOutput(
            self, "ecs-cluster-name", value=self.cluster_construct.cluster.cluster_name
        )
