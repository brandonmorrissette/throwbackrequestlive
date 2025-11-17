# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    runtime_construct: MagicMock
    runtime_construct_args: MagicMock
    route53_construct: MagicMock
    route53_construct_args: MagicMock


@pytest.fixture(scope="module")
def mocked_runtime_stack_args(config: Config):
    # pylint: disable=duplicate-code
    return RuntimeStackArgs(
        config,
        vpc=MagicMock(),
        certificate=MagicMock(),
        policy=MagicMock(),
        cluster=MagicMock(),
        bucket=MagicMock(),
        db_instance=MagicMock(),
        gateway_security_group=MagicMock(),
    )


@pytest.fixture(scope="module")
def mocked_runtime_stack(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    app: cdk.App,
    mocked_runtime_stack_args: RuntimeStackArgs,
):
    with patch(
        "infra.stacks.runtime.RuntimeConstruct"
    ) as mock_runtime_construct, patch(
        "infra.stacks.runtime.RuntimeConstructArgs"
    ) as mock_runtime_construct_args, patch(
        "infra.stacks.runtime.Route53Construct"
    ) as mock_route53_construct, patch(
        "infra.stacks.runtime.Route53ConstructArgs"
    ) as mock_route53_construct_args:
        yield RuntimeStack(app, mocked_runtime_stack_args), Mocks(
            mock_runtime_construct,
            mock_runtime_construct_args,
            mock_route53_construct,
            mock_route53_construct_args,
        )


def test_default_id(
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    config: Config,
):
    stack, _ = mocked_runtime_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-runtime"


def test_runtime_construct(
    mocked_runtime_stack_args: RuntimeStackArgs,
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_runtime_stack

    mocks.runtime_construct.assert_called_once_with(
        stack,
        mocks.runtime_construct_args.return_value,
    )

    mocks.runtime_construct_args.assert_called_once_with(
        config=config,
        vpc=mocked_runtime_stack_args.vpc,
        certificate=mocked_runtime_stack_args.certificate,
        policy=mocked_runtime_stack_args.policy,
        cluster=mocked_runtime_stack_args.cluster,
        db_instance=mocked_runtime_stack_args.db_instance,
        runtime_variables={
            "PROJECT_NAME": str(config.project_name),
            "ENVIRONMENT": str(config.environment_name),
        },
    )


def test_route53_construct(
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_runtime_stack

    mocks.route53_construct.assert_called_once_with(
        stack,
        mocks.route53_construct_args.return_value,
    )

    mocks.route53_construct_args.assert_called_once_with(
        config,
    )
