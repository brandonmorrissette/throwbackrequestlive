# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import assertions

from infra.config import Config
from infra.stacks.network import NetworkStack, NetworkStackArgs


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config) -> NetworkStack:
    return NetworkStack(app, NetworkStackArgs(config))


@pytest.fixture
def subnets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::EC2::Subnet")


def test_vpc(vpcs: Mapping[str, Any]) -> None:
    assert len(vpcs) == 1


def test_certificate(certificates: Mapping[str, Any]) -> None:
    assert len(certificates) == 1


def test_cfn_output(template: assertions.Template, subnets: Mapping[str, Any]) -> None:
    subnet_id_output = template.find_outputs("subnetid")
    assert subnet_id_output
    assert subnet_id_output["subnetid"]["Value"]["Ref"] == next(
        key for key in subnets.keys() if "privatesubnet" in key.lower()
    )
