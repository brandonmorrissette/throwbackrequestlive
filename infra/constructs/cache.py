"""
This module contains the CacheConstruct class, which sets up a cache cluster
within a specified VPC. The construct includes security group configuration and subnet group
creation for the cache cluster.

Classes:
    CacheConstruct: A construct that sets up a cache cluster.

Usage example:
    cache_construct = CacheConstruct(scope, vpc, config)
"""

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class CacheConstruct(Construct):
    """
    A construct that sets up a cache cluster.

    Attributes:
        cluster: The cache cluster.

    Methods:
        __init__: Initializes the CacheConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        vpc: ec2.Vpc,
        config: Config,
        id: str | None = None,
        suffix: str | None = "cert",
    ):
        """
        Initializes the CacheConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            vpc (ec2.Vpc): The VPC in which to create the cache cluster.
            config (Config): Configuration object.
            id (str, optional): The ID of the construct. Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): Suffix for resource names. Defaults to "cert".
        """
        super().__init__(scope, config, id, suffix)

        security_group = ec2.SecurityGroup(self, "RedisSG", vpc=vpc)

        security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(6379),
            "Allow Redis access",
        )

        subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            description="Subnet group for Redis",
        )

        self.cluster = elasticache.CfnCacheCluster(
            self,
            "RedisCluster",
            cache_node_type="cache.t2.micro",
            engine="redis",
            num_cache_nodes=1,
            vpc_security_group_ids=[security_group.security_group_id],
            cache_subnet_group_name=subnet_group.ref,
        )
