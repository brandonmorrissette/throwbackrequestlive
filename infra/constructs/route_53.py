"""
This module contains the Route53Construct class, which sets up Route 53 alias records
for a specified hosted zone and load balancer.

Classes:
    Route53Construct: A construct that sets up Route 53 alias records.

Usage example:
    route53_construct = Route53Construct(scope, config, hosted_zone, http_api)
"""

from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from aws_cdk import aws_apigatewayv2 as apigwv2

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class Route53ConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the Route53Construct class.

    Attributes:
        config: Configuration object.
        uid: Unique identifier for the resource.
            Defaults to route53.
        prefix: Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-".
        hosted_zone (route53.IHostedZone): The Route 53 hosted zone.
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        hosted_zone: route53.IHostedZone,
        domain_name: apigwv2.IDomainName,
        uid: str = "route53",
        prefix: str = "",
    ) -> None:
        super().__init__(config=config, uid=uid, prefix=prefix)
        self.hosted_zone = hosted_zone
        self.domain_name = domain_name


class Route53Construct(Construct):
    """
    A construct that sets up Route 53 alias records.

    Methods:
        __init__: Initializes the Route53Construct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: Route53ConstructArgs,
    ) -> None:
        """
        Initializes the Route53Construct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (Route53ConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        route53.ARecord(
            self,
            "api-gateway-alias-record",
            zone=args.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    args.domain_name.regional_domain_name,
                    args.domain_name.regional_hosted_zone_id,
                )
            ),
        )

        route53.ARecord(
            self,
            "gateway-alias-record-www",
            record_name="www",
            zone=args.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    args.domain_name.regional_domain_name,
                    args.domain_name.regional_hosted_zone_id,
                )
            ),
        )

        route53.AaaaRecord(
            self,
            "api-gateway-alias-record-aaaa",
            zone=args.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    args.domain_name.regional_domain_name,
                    args.domain_name.regional_hosted_zone_id,
                )
            ),
        )


