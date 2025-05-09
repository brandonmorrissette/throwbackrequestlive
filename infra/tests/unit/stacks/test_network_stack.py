# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.stacks.network import NetworkStack, NetworkStackArgs


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    vpc_construct: MagicMock
    vpc_construct_args: MagicMock
    cert_construct: MagicMock
    cert_construct_args: MagicMock
    cfn_output: MagicMock


@pytest.fixture(scope="module")
def mocked_network_stack(app: cdk.App, config: Config):
    with patch("infra.stacks.network.VpcConstruct") as mock_vpc_construct, patch(
        "infra.stacks.network.VpcConstructArgs"
    ) as mock_vpc_construct_args, patch(
        "infra.stacks.network.CertConstruct"
    ) as mock_cert_construct, patch(
        "infra.stacks.network.CertConstructArgs"
    ) as mock_cert_construct_args, patch(
        "infra.stacks.network.CfnOutput"
    ) as mock_cfn_output:
        yield NetworkStack(app, NetworkStackArgs(config)), Mocks(
            mock_vpc_construct,
            mock_vpc_construct_args,
            mock_cert_construct,
            mock_cert_construct_args,
            mock_cfn_output,
        )


def test_default_id(
    mocked_network_stack: tuple[NetworkStack, Mocks],
    config: Config,
):
    stack, _ = mocked_network_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-network"


def test_vpc_construct(
    mocked_network_stack: tuple[NetworkStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_network_stack

    mocks.vpc_construct_args.assert_called_once_with(config)
    mocks.vpc_construct.assert_called_once_with(
        stack, mocks.vpc_construct_args.return_value
    )


def test_cert_construct(
    mocked_network_stack: tuple[NetworkStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_network_stack

    mocks.cert_construct_args.assert_called_once_with(config)
    mocks.cert_construct.assert_called_once_with(
        stack, mocks.cert_construct_args.return_value
    )


def test_cfn_output(
    mocked_network_stack: tuple[NetworkStack, Mocks],
):
    stack, mocks = mocked_network_stack

    mocks.cfn_output.assert_called_once_with(
        stack,
        "subnetid",
        value=mocks.vpc_construct.return_value.vpc.select_subnets.return_value.subnet_ids[
            0
        ],
    )
