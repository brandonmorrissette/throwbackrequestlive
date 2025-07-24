# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import ANY, MagicMock, call, patch

import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.vpc import VpcConstruct, VpcConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def mock_vpc_construct(config: Config, stack: Stack):
    with patch("infra.constructs.vpc.ec2") as mock_ec2:
        yield VpcConstruct(stack, VpcConstructArgs(config)), mock_ec2


def test_construct_inheritance():
    assert issubclass(VpcConstruct, Construct)


def test_default_id(mock_vpc_construct: tuple[VpcConstruct, MagicMock], config: Config):
    construct, _ = mock_vpc_construct
    assert construct.node.id == f"{config.project_name}-{config.environment_name}-vpc"


def test_vpc_creation(mock_vpc_construct: tuple[VpcConstruct, MagicMock]):
    construct, mock_ec2 = mock_vpc_construct

    mock_ec2.Vpc.assert_called_once_with(
        construct,
        ANY,
        max_azs=1,
        nat_gateways=0,
        subnet_configuration=[
            mock_ec2.SubnetConfiguration.return_value,
            mock_ec2.SubnetConfiguration.return_value,
        ],
    )

    mock_ec2.SubnetConfiguration.assert_has_calls(
        [
            call(name="public", subnet_type=mock_ec2.SubnetType.PUBLIC, cidr_mask=24),
            call(
                name="isolated",
                subnet_type=mock_ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=24,
            ),
        ]
    )


def test_endpoints_added(mock_vpc_construct: tuple[VpcConstruct, MagicMock]):
    _, mock_ec2 = mock_vpc_construct

    mock_ec2.Vpc.return_value.add_gateway_endpoint.assert_has_calls(
        [
            call("S3Endpoint", service=mock_ec2.GatewayVpcEndpointAwsService.S3),
        ]
    )

    mock_ec2.Vpc.return_value.add_interface_endpoint.assert_has_calls(
        [
            call("EcrEndpoint", service=mock_ec2.InterfaceVpcEndpointAwsService.ECR),
            call(
                "EcrDockerEndpoint",
                service=mock_ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            ),
            call(
                "SecretsManagerEndpoint",
                service=mock_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            ),
            call(
                "SsmEndpoint",
                service=mock_ec2.InterfaceVpcEndpointAwsService.SSM,
            ),
            call(
                "CloudWatchLogsEndpoint",
                service=mock_ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            ),
        ]
    )
