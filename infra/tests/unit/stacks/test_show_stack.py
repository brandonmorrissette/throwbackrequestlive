# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.stacks.show import ShowStack, ShowStackArgs


@pytest.fixture(scope="module")
def args(config: Config, vpc: ec2.IVpc) -> ShowStackArgs:
    return ShowStackArgs(
        config=config,
        vpc=vpc,
    )


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    cache_construct: MagicMock
    cache_construct_args: MagicMock


@pytest.fixture(scope="module")
def mock_show_stack(app: cdk.App, args: ShowStackArgs) -> tuple[ShowStack, Mocks]:
    with patch("infra.stacks.show.CacheConstruct") as mock_cache_construct, patch(
        "infra.stacks.show.CacheConstructArgs"
    ) as mock_cache_construct_args:
        return ShowStack(app, args), Mocks(
            cache_construct=mock_cache_construct,
            cache_construct_args=mock_cache_construct_args,
        )


def test_default_id(
    mock_show_stack: tuple[ShowStack, Mocks],
    config: Config,
):
    stack, _ = mock_show_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-show"


def test_cache_construct(
    mock_show_stack: tuple[ShowStack, Mocks],
    vpc: MagicMock,
    config: Config,
):
    stack, mocks = mock_show_stack

    mocks.cache_construct_args.assert_called_once_with(config, vpc)
    mocks.cache_construct.assert_called_once_with(
        stack, mocks.cache_construct_args.return_value
    )
