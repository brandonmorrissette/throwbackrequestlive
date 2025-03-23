# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import assertions
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.stacks.compute import ComputeStack, ComputeStackArgs


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config, vpc: ec2.Vpc) -> ComputeStack:
    return ComputeStack(app, ComputeStackArgs(config, vpc))


def test_cluster(clusters: Mapping[str, Any]) -> None:
    assert len(clusters) == 1


def test_cfn_output(template: assertions.Template, clusters: Mapping[str, Any]) -> None:
    cluster_name_output = template.find_outputs("ecsclustername")
    assert cluster_name_output
    assert cluster_name_output["ecsclustername"]["Value"] == {
        "Ref": next(iter(clusters.keys()))
    }
