from config import Config
from constructs import Construct
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
    ):
        super().__init__(scope, config, suffix="runtime")

        fargate_service = RuntimeEcsConstruct(
            self,
            config,
            certificate=certificate,
            vpc=vpc,
            db_instance=db_instance,
        ).runtime_service

        Route53Construct(
            self,
            "route-53",
            hosted_zone=hosted_zone,
            load_balancer=fargate_service.load_balancer,
        )
