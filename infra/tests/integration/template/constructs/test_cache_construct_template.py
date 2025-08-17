# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.constructs.cache import CacheConstruct, CacheConstructArgs
from infra.stacks.stack import Stack
from infra.tests import conftest


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config, vpc: ec2.Vpc) -> CacheConstruct:
    return CacheConstruct(stack, CacheConstructArgs(config, vpc))


def test_security_group(
    security_groups: Mapping[str, Any], vpcs: Mapping[str, Any], config: Config
):
    assert len(security_groups) == 1
    security_group = next(iter(security_groups.values()))

    vpc_id = next(iter(vpcs.keys()))

    assert security_group["Properties"]["VpcId"]["Ref"] == vpc_id
    assert (
        security_group["Properties"]["GroupDescription"] == f"{conftest.STACK_NAME}/"
        f"{config.project_name}-{config.environment_name}-cache/redis-security-group"
    )

    ingress_rule = next(iter(security_group["Properties"]["SecurityGroupIngress"]))
    assert ingress_rule["FromPort"] == 6379
    assert ingress_rule["ToPort"] == 6379
    assert ingress_rule["IpProtocol"] == "tcp"
    assert ingress_rule["Description"] == "Allow Redis access"
    assert ingress_rule["CidrIp"]["Fn::GetAtt"] == [vpc_id, "CidrBlock"]


def test_subnet_group(subnet_groups: Mapping[str, Any], vpcs: Mapping[str, Any]):
    assert len(subnet_groups) == 1
    subnet_group = next(iter(subnet_groups.values()))

    vpcs = next(iter(vpcs.values()))

    assert subnet_group["Properties"]["Description"] == "Subnet group for Redis"


def test_cache_cluster(
    cache_clusters: Mapping[str, Any],
    security_groups: Mapping[str, Any],
    subnet_groups: Mapping[str, Any],
):
    assert len(cache_clusters) == 1
    cache_cluster = next(iter(cache_clusters.values()))
    security_group_id = next(iter(security_groups.keys()))
    subnet_group_id = next(iter(subnet_groups.keys()))

    assert cache_cluster["Properties"]["CacheNodeType"] == "cache.t2.micro"
    assert cache_cluster["Properties"]["Engine"] == "redis"
    assert cache_cluster["Properties"]["NumCacheNodes"] == 1
    assert next(iter(cache_cluster["Properties"]["VpcSecurityGroupIds"]))[
        "Fn::GetAtt"
    ] == [security_group_id, "GroupId"]
    assert cache_cluster["Properties"]["CacheSubnetGroupName"]["Ref"] == subnet_group_id
