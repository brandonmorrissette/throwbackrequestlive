# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53

from infra.config import Config
from infra.constructs.route_53 import Route53Construct, Route53ConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def hosted_zone(stack: Stack) -> route53.HostedZone:
    return route53.HostedZone(stack, "MockHostedZone", zone_name="example.com")


@pytest.fixture(scope="module")
def load_balancer(stack: Stack, vpc: ec2.Vpc) -> elbv2.ApplicationLoadBalancer:
    return elbv2.ApplicationLoadBalancer(
        stack,
        "MockLoadBalancer",
        vpc=vpc,
    )


@pytest.fixture(scope="module")
def route53_construct_args(
    config: Config,
    hosted_zone: route53.HostedZone,
    load_balancer: elbv2.ApplicationLoadBalancer,
) -> Route53ConstructArgs:
    return Route53ConstructArgs(
        config=config,
        hosted_zone=hosted_zone,
        load_balancer=load_balancer,
    )


@pytest.fixture(scope="module", autouse=True)
def construct(
    stack: Stack,
    route53_construct_args: Route53ConstructArgs,
) -> Route53Construct:
    return Route53Construct(
        stack,
        route53_construct_args,
    )


def test_alias_record(
    record_sets: Mapping[str, Any],
    load_balancers: Mapping[str, Any],
    hosted_zones: Mapping[str, Any],
) -> None:
    alias_record = next(
        record
        for record in record_sets.values()
        if record["Properties"]["Name"] == "example.com."
    )
    assert alias_record
    assert alias_record["Properties"]["AliasTarget"]["DNSName"]["Fn::Join"][1][1][
        "Fn::GetAtt"
    ] == [next(iter(load_balancers.keys())), "DNSName"]

    assert alias_record["Properties"]["HostedZoneId"]["Ref"] == next(
        iter(hosted_zones.keys())
    )


def test_alias_www_record(
    record_sets: Mapping[str, Any],
    load_balancers: Mapping[str, Any],
    hosted_zones: Mapping[str, Any],
) -> None:
    alias_record = next(
        record
        for record in record_sets.values()
        if record["Properties"]["Name"] == "www.example.com."
    )
    assert alias_record
    assert alias_record["Properties"]["AliasTarget"]["DNSName"]["Fn::Join"][1][1][
        "Fn::GetAtt"
    ] == [next(iter(load_balancers.keys())), "DNSName"]

    assert alias_record["Properties"]["HostedZoneId"]["Ref"] == next(
        iter(hosted_zones.keys())
    )
