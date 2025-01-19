from aws_cdk import aws_route53 as route53, aws_route53_targets as targets
from constructs import Construct


class Route53Construct(Construct):
    def __init__(self, scope: Construct, id: str, hosted_zone, load_balancer) -> None:
        super().__init__(scope, id)

        route53.ARecord(
            self, "alias-record",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(load_balancer))
        )

        route53.ARecord(
            self, "alias-record-www",
            zone=hosted_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(load_balancer))
        )
