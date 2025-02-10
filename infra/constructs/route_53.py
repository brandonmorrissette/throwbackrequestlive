from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from config import Config
from constructs import Construct


class Route53Construct(Construct):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        hosted_zone,
        load_balancer,
        id: str | None = None,
        suffix: str | None = "route53",
    ) -> None:

        super().__init__(scope, config, id, suffix)

        route53.ARecord(
            self,
            "alias-record",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(load_balancer)
            ),
        )

        route53.ARecord(
            self,
            "alias-record-www",
            zone=hosted_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(load_balancer)
            ),
        )
