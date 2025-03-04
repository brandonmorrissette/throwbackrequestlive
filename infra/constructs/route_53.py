"""
This module contains the Route53Construct class, which sets up Route 53 alias records
for a specified hosted zone and load balancer.

Classes:
    Route53Construct: A construct that sets up Route 53 alias records.

Usage example:
    route53_construct = Route53Construct(scope, config, hosted_zone, load_balancer)
"""

from dataclasses import dataclass

from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


@dataclass
class Route53ConstructArgs:
    """
    A class that defines properties for the Route53Construct class.

    Attributes:
        hosted_zone (route53.IHostedZone): The Route 53 hosted zone.
        load_balancer (elbv2.ILoadBalancerV2): The load balancer.
    """

    hosted_zone: route53.IHostedZone
    load_balancer: elbv2.ILoadBalancerV2


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
        args: Route53ConstructArgs,
        construct_id: str | None = None,
    ) -> None:
        """
        Initializes the Route53Construct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            hosted_zone (route53.IHostedZone): The Route 53 hosted zone.
            load_balancer (elbv2.ILoadBalancerV2): The load balancer.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-route53".
        """
        super().__init__(scope, config, construct_id, "route53")

        route53.ARecord(
            self,
            "alias-record",
            zone=args.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(args.load_balancer)
            ),
        )

        route53.ARecord(
            self,
            "alias-record-www",
            zone=args.hosted_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(args.load_balancer)
            ),
        )
