# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import ANY, MagicMock, patch

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
        max_azs=2,
    )
