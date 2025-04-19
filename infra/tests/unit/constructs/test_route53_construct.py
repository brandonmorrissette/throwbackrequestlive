# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.route_53 import Route53Construct, Route53ConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def route53_construct_args(config: Config) -> Route53ConstructArgs:
    return Route53ConstructArgs(
        config, hosted_zone=MagicMock(), load_balancer=MagicMock()
    )


@pytest.fixture(scope="module")
def mock_route53_construct(stack: Stack, route53_construct_args: MagicMock):
    with patch("infra.constructs.route_53.route53") as mock_route53, patch(
        "infra.constructs.route_53.targets"
    ) as mock_targets:
        yield Route53Construct(
            stack, route53_construct_args
        ), mock_route53, mock_targets


def test_construct_inheritance():
    assert issubclass(Route53Construct, Construct)


def test_default_id(
    mock_route53_construct: tuple[Route53Construct, MagicMock, MagicMock],
    config: Config,
):
    construct, _, _ = mock_route53_construct
    assert (
        construct.node.id == f"{config.project_name}-{config.environment_name}-route53"
    )


def test_target_created(
    mock_route53_construct: tuple[Route53Construct, MagicMock, MagicMock],
    route53_construct_args: MagicMock,
):
    _, mock_route53, mock_targets = mock_route53_construct

    mock_targets.LoadBalancerTarget.assert_called_once_with(
        route53_construct_args.load_balancer
    )
    mock_route53.RecordTarget.from_alias.assert_called_once_with(
        mock_targets.LoadBalancerTarget.return_value
    )


def test_alias_record_creation(
    mock_route53_construct: tuple[Route53Construct, MagicMock, MagicMock],
    route53_construct_args: MagicMock,
):
    construct, mock_route53, _ = mock_route53_construct

    mock_route53.ARecord.assert_any_call(
        construct,
        "alias-record",
        zone=route53_construct_args.hosted_zone,
        target=mock_route53.RecordTarget.from_alias.return_value,
    )


def test_alias_www_record_creation(
    mock_route53_construct: tuple[Route53Construct, MagicMock, MagicMock],
    route53_construct_args: MagicMock,
):
    construct, mock_route53, _ = mock_route53_construct

    mock_route53.ARecord.assert_any_call(
        construct,
        "alias-record-www",
        zone=route53_construct_args.hosted_zone,
        record_name="www",
        target=mock_route53.RecordTarget.from_alias.return_value,
    )
