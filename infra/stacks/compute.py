"""
This module defines the ComputeStack class, which sets up the compute resources for the application.

It creates an ECS cluster using the provided VPC and configuration.
"""

from dataclasses import dataclass

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infra.config import Config
from infra.constructs.cluster import ClusterConstruct, ClusterConstructArgs
from infra.stacks.stack import Stack, StackArgs


@dataclass
class ComputeStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the ComputeStack.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the ECS cluster.
        uid (str): The ID of the stack.
            Default is "compute".
        prefix (str): The prefix for the stack name.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        vpc: ec2.Vpc,
        uid: str = "compute",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc


class ComputeStack(Stack):
    """
    This stack sets up the compute resources for the application.

    It creates an ECS cluster using the provided VPC and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: ComputeStackArgs,
    ) -> None:
        """
        Initialize the ComputeStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (ComputeStackArgs): The arguments for the stack.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.cluster_construct = ClusterConstruct(
            self, ClusterConstructArgs(args.config, args.vpc)
        )

        CfnOutput(
            self, "ecsclustername", value=self.cluster_construct.cluster.cluster_name
        )
