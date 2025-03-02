"""
This module defines the NetworkStack class, which sets up the network resources for the application.

It creates VPC and Certificate constructs using the provided configuration.
"""

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs import Construct
from constructs.cert import CertConstruct
from constructs.vpc import VpcConstruct
from stacks.stack import Stack


class NetworkStack(Stack):
    """
    This stack sets up the network resources for the application.

    It creates VPC and Certificate constructs using the provided configuration.
    """

    def __init__(
        self,
        scope: Construct,
        config: Config,
        stack_id: str | None = None,
    ) -> None:
        """
        Initialize the NetworkStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            config (Config): The configuration object containing stack settings.
            stack_id (str, optional): The ID of the stack.
                Defaults to f"{config.project_name}-{config.environment_name}-network".
        """
        super().__init__(scope, config, stack_id, "network")

        self.vpc_constrcut = VpcConstruct(self, config)
        self.cert_construct = CertConstruct(self, config)

        CfnOutput(
            self,
            "subnet-id",
            value=self.vpc_constrcut.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids[0],
        )
