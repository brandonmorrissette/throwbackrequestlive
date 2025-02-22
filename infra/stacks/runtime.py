from aws_cdk import aws_iam as iam
from config import Config
from constructs.construct import Construct
from constructs.route_53 import Route53Construct
from constructs.runtime_ecs import RuntimeEcsConstruct
from stacks.stack import Stack


class RuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        certificate: str,
        hosted_zone: str,
        db_instance,
        vpc,
        cache_cluster,
        runtime_policy: iam.ManagedPolicy,
        id: str | None = None,
        suffix: str | None = "runtime",
    ):
        super().__init__(scope, config, id, suffix)

        runtime_construct = RuntimeEcsConstruct(
            self,
            config,
            certificate=certificate,
            vpc=vpc,
            db_instance=db_instance,
            cache_cluster=cache_cluster,
            runtime_policy=runtime_policy,
        )

        Route53Construct(
            self,
            config,
            hosted_zone=hosted_zone,
            load_balancer=runtime_construct.load_balancer,
        )
