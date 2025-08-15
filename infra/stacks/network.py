"""
This module defines the NetworkStack class, which sets up the network resources for the application.

It creates VPC and Certificate constructs using the provided configuration.
"""

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infra.config import Config
from infra.constructs.cert import CertConstruct, CertConstructArgs
from infra.constructs.load_balancer import (
    LoadBalancerConstruct,
    LoadBalancerConstructArgs,
)
from infra.constructs.vpc import VpcConstruct, VpcConstructArgs
from infra.stacks.stack import Stack, StackArgs


class NetworkStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the NetworkStack.

    Attributes:
        config (Config): Configuration object.
        uid (str): The ID of the stack.
            Default is "network".
        prefix (str): The prefix for the stack name.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        uid: str = "network",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


class NetworkStack(Stack):
    """
    This stack sets up the network resources for the application.

    It creates VPC and Certificate constructs using the provided configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: NetworkStackArgs,
    ) -> None:
        """
        Initialize the NetworkStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (NetworkStackArgs): The arguments for the stack.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.vpc_construct = VpcConstruct(self, VpcConstructArgs(args.config))
        self.cert_construct = CertConstruct(self, CertConstructArgs(args.config))
        self.load_balancer_construct = LoadBalancerConstruct(
            self,
            LoadBalancerConstructArgs(
                args.config,
                self.vpc_construct.vpc,
                self.cert_construct.certificate,
                args.uid,
                args.prefix,
            ),
        )

        CfnOutput(
            self,
            "subnetid",
            value=self.vpc_construct.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PUBLIC
            ).subnet_ids[0],
        )
