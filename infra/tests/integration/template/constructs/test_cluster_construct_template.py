# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.constructs.cluster import ClusterConstruct, ClusterConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config, vpc: ec2.Vpc) -> ClusterConstruct:
    return ClusterConstruct(stack, ClusterConstructArgs(config, vpc))


def test_cluster(clusters: Mapping[str, Any], vpcs: Mapping[str, Any]):
    assert len(clusters) == 1
    assert len(vpcs) == 1
