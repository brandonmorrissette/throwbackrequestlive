# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import pytest
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infra.config import Config
from infra.constructs.cluster import ClusterConstruct, ClusterConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def vpc(stack: Stack):
    vpc = ec2.Vpc(stack, "Vpc")
    return vpc


@pytest.fixture(scope="module")
def mock_cluster_construct(vpc: ec2.Vpc, config: Config, stack: Stack):
    with patch("infra.constructs.cluster.ecs") as mock_ecs:
        construct = ClusterConstruct(stack, ClusterConstructArgs(config, vpc))

        yield construct, mock_ecs


def test_construct_inheritance():
    assert issubclass(ClusterConstruct, Construct)


def test_default_id(
    mock_cluster_construct: tuple[ClusterConstruct, MagicMock], config: Config
):
    cluster_construct, _ = mock_cluster_construct

    assert (
        cluster_construct.node.id
        == f"{config.project_name}-{config.environment_name}-cluster"
    )


def test_cluster_creation(
    vpc: ec2.Vpc,
    mock_cluster_construct: tuple[ClusterConstruct, MagicMock],
    config: Config,
):
    cluster_construct, mock_ecs = mock_cluster_construct

    mock_ecs.Cluster.assert_called_once_with(
        cluster_construct,
        f"{config.project_name}-{config.environment_name}-cluster",
        vpc=vpc,
    )
