"""
This module contains the VpcConstruct class, 
which sets up a VPC with a specified number of availability zones.

Classes:
    VpcConstruct: A construct that sets up a VPC.

Usage example:
    vpc_construct = VpcConstruct(scope, config)
"""

from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs.construct import Construct
from resources.resource import Resource
from stacks.stack import Stack


class VpcConstruct(Construct, Resource):
    """
    A construct that sets up a VPC.

    Attributes:
        vpc: The VPC.

    Methods:
        __init__: Initializes the VpcConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        config: Config,
        construct_id: str | None = None,
    ) -> None:
        """
        Initializes the VpcConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-vpc".
        """
        super().__init__(scope, config, construct_id, "vpc")

        self.vpc = ec2.Vpc(self, self.id, max_azs=2)
