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

from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class CacheConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the CacheConstruct class.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the cache cluster.
        uid (str): The ID of the construct.
            Default is "cache".
        prefix (str): The prefix for the construct ID.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(self, config, vpc: ec2.Vpc, uid: str = "cache", prefix: str = ""):
        super().__init__(config, uid, prefix)
        self.vpc = vpc


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
        args: CacheConstructArgs,
    ):
        """
        Initializes the CacheConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (CacheConstructArgs): Arguments containing the VPC and configuration.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        security_group = ec2.SecurityGroup(self, "RedisSG", vpc=args.vpc)

        security_group.add_ingress_rule(
            ec2.Peer.ipv4(args.vpc.vpc_cidr_block),
            ec2.Port.tcp(6379),
            "Allow Redis access",
        )

        subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            subnet_ids=[subnet.subnet_id for subnet in args.vpc.private_subnets],
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
