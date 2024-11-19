from aws_cdk import Stack
from constructs import Construct
from constructs.runtime_ecs import RuntimeEcsConstruct
from constructs.route_53 import Route53Construct


class AppStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster_arn: str,
        certificate_arn: str,
        hosted_zone_id: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        fargate_service = RuntimeEcsConstruct(
            self, "RuntimeEcs", cluster=cluster_arn, certificate=certificate_arn
        ).fargate_service

        Route53Construct(
            self,
            "Route53",
            hosted_zone=hosted_zone_id,
            load_balancer=fargate_service.load_balancer,
        )
