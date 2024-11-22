from constructs import Construct
from constructs.runtime_ecs import RuntimeEcsConstruct
from constructs.route_53 import Route53Construct
from .stack import Stack

class RuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster: str,
        certificate: str,
        hosted_zone: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        fargate_service = RuntimeEcsConstruct(
            self, "RuntimeEcs", cluster=cluster, certificate=certificate
        ).fargate_service

        Route53Construct(
            self,
            "Route53",
            hosted_zone=hosted_zone,
            load_balancer=fargate_service.load_balancer,
        )
