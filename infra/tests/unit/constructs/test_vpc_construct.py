# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

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


def test_vpc_creation(
    config: Config, mock_vpc_construct: tuple[VpcConstruct, MagicMock]
):
    construct, mock_ec2 = mock_vpc_construct

    mock_ec2.Vpc.assert_called_once_with(
        construct,
        f"{config.project_name}-{config.environment_name}-vpc",
        max_azs=2,
        nat_gateways=0,
        subnet_configuration=[
            mock_ec2.SubnetConfiguration.return_value,
            mock_ec2.SubnetConfiguration.return_value,
        ],
        ip_protocol=mock_ec2.IpProtocol.IPV4_ONLY,
    )


def test_private_subnets(mock_vpc_construct: tuple[VpcConstruct, MagicMock]):
    construct, mock_ec2 = mock_vpc_construct

    mock_ec2.SubnetConfiguration.assert_any_call(
        name="private",
        subnet_type=mock_ec2.SubnetType.PRIVATE_WITH_EGRESS,
        cidr_mask=24,
    )
    assert (
        construct.private_subnets
        == mock_ec2.Vpc.return_value.select_subnets.return_value.subnets
    )


def test_public_subnets(mock_vpc_construct: tuple[VpcConstruct, MagicMock]):
    construct, mock_ec2 = mock_vpc_construct

    mock_ec2.SubnetConfiguration.assert_any_call(
        name="public",
        subnet_type=mock_ec2.SubnetType.PUBLIC,
        cidr_mask=24,
    )
    assert (
        construct.public_subnets
        == mock_ec2.Vpc.return_value.select_subnets.return_value.subnets
    )
