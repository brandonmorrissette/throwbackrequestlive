from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from config import Config
from constructs.construct import Construct


class CacheConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        vpc,
        config: Config,
        id: str | None = None,
        suffix: str | None = "cert",
    ):
        super().__init__(scope, config, id, suffix)

        redis_sg = ec2.SecurityGroup(self, "RedisSG", vpc=vpc)

        redis_sg.add_ingress_rule(
            # MUST BE CHANGED TO ALLOW ONLY THE APPLICATION TO ACCESS
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(6379),
            "Allow Redis access",
        )

        subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            description="Subnet group for Redis",
        )

        self.cache_cluster = elasticache.CfnCacheCluster(
            self,
            "RedisCluster",
            cache_node_type="cache.t2.micro",
            engine="redis",
            num_cache_nodes=1,
            vpc_security_group_ids=[redis_sg.security_group_id],
            cache_subnet_group_name=subnet_group.ref,
        )
