# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import pytest
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infra.config import Config
from infra.constructs.cache import CacheConstruct, CacheConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def mock_cache_construct(vpc: ec2.Vpc, config: Config, stack: Stack):
    with patch("infra.constructs.cache.ec2") as mock_ec2, patch(
        "infra.constructs.cache.elasticache"
    ) as mock_elasticache:
        construct = CacheConstruct(stack, CacheConstructArgs(config, vpc))

        yield construct, mock_ec2, mock_elasticache


def test_construct_inheritance():
    assert issubclass(CacheConstruct, Construct)


def test_default_id(
    mock_cache_construct: tuple[CacheConstruct, MagicMock, MagicMock], config: Config
):
    cache_construct, _, _ = mock_cache_construct
    assert (
        cache_construct.node.id
        == f"{config.project_name}-{config.environment_name}-cache"
    )


def test_security_group_creation(
    vpc: ec2.Vpc, mock_cache_construct: tuple[CacheConstruct, MagicMock, MagicMock]
):
    cache_construct, mock_ec2, _ = mock_cache_construct

    mock_ec2.SecurityGroup.assert_called_once_with(
        cache_construct, "redis-security-group", vpc=vpc
    )

    mock_ec2.SecurityGroup.return_value.add_ingress_rule.assert_called_once_with(
        mock_ec2.Peer.ipv4(vpc.vpc_cidr_block),
        mock_ec2.Port.tcp(6379),
        "Allow Redis access",
    )


def test_subnet_group_creation(
    vpc: ec2.Vpc, mock_cache_construct: tuple[CacheConstruct, MagicMock, MagicMock]
):
    cache_construct, _, mock_elasticache = mock_cache_construct

    mock_elasticache.CfnSubnetGroup.assert_called_once_with(
        cache_construct,
        "redis-subnet-group",
        description="Subnet group for Redis",
        subnet_ids=[subnet.subnet_id for subnet in vpc.public_subnets],
    )


def test_cache_cluster_creation(
    mock_cache_construct: tuple[CacheConstruct, MagicMock, MagicMock],
):
    cache_construct, mock_ec2, mock_elasticache = mock_cache_construct

    mock_elasticache.CfnCacheCluster.assert_called_once_with(
        # pylint: disable=duplicate-code
        cache_construct,
        "redis-cluster",
        cache_node_type="cache.t2.micro",
        engine="redis",
        engine_version="6.2",
        num_cache_nodes=1,
        vpc_security_group_ids=[mock_ec2.SecurityGroup.return_value.security_group_id],
        cache_subnet_group_name=mock_elasticache.CfnSubnetGroup.return_value.ref,
    )
