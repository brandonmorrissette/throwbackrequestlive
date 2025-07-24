"""
This module contains the VpcConstruct class,
which sets up a VPC with a specified number of availability zones.

Classes:
    VpcConstruct: A construct that sets up a VPC.

Usage example:
    vpc_construct = VpcConstruct(scope, config)
"""

from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class VpcConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the VpcConstruct class.

    Attributes:
        config: Configuration object.
        uid: Unique identifier for the resource.
            Defaults to "vpc".
        prefix: Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-vpc".
    """

    def __init__(
        self,
        config: Config,
        uid: str = "vpc",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


class VpcConstruct(Construct):
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
        args: VpcConstructArgs,
    ) -> None:
        """
        Initializes the VpcConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (VpcConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        self.vpc = ec2.Vpc(
            self,
            f"{args.config.project_name}-{args.config.environment_name}-vpc",
            max_azs=1,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        self.vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
        )
        self.vpc.add_interface_endpoint(
            "EcrEndpoint", service=ec2.InterfaceVpcEndpointAwsService.ECR
        )

        self.vpc.add_interface_endpoint(
            "EcrDockerEndpoint", service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )
        self.vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )
        self.vpc.add_interface_endpoint(
            "SsmEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SSM
        )
        self.vpc.add_interface_endpoint(
            "CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
        )
