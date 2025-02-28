"""
This module contains the Route53Construct class, which sets up Route 53 alias records
for a specified hosted zone and load balancer.

Classes:
    Route53Construct: A construct that sets up Route 53 alias records.

Usage example:
    route53_construct = Route53Construct(scope, config, hosted_zone, load_balancer)
"""

from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class Route53Construct(Construct):
    """
    A construct that sets up Route 53 alias records.

    Methods:
        __init__: Initializes the Route53Construct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        config: Config,
        hosted_zone,
        load_balancer,
        id: str | None = None,
        suffix: str | None = "route53",
    ) -> None:
        """
        Initializes the Route53Construct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            hosted_zone (route53.IHostedZone): The Route 53 hosted zone.
            load_balancer (elbv2.ILoadBalancerV2): The load balancer.
            id (str, optional): The ID of the construct. Defaults to f"{config.project_name}-{config.environment_name}".
            suffix (str, optional): Suffix for resource names. Defaults to "route53".
        """
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
