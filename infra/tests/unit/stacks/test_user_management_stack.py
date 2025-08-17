# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.stacks.user_management import UserManagementStack, UserManagementStackArgs


@pytest.fixture(scope="module")
def args(config: Config) -> UserManagementStackArgs:
    return UserManagementStackArgs(config=config)


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    user_pool_construct: MagicMock
    user_pool_construct_args: MagicMock
    superuser_construct: MagicMock
    superuser_construct_args: MagicMock


@pytest.fixture(scope="module")
def mocked_user_management_stack(
    app: cdk.App, args: UserManagementStackArgs
) -> tuple[UserManagementStack, Mocks]:
    with patch(
        "infra.stacks.user_management.UserPoolConstruct"
    ) as mock_user_pool_construct, patch(
        "infra.stacks.user_management.UserPoolConstructArgs"
    ) as mock_user_pool_construct_args, patch(
        "infra.stacks.user_management.SuperUserConstruct"
    ) as mock_superuser_construct, patch(
        "infra.stacks.user_management.SuperUserConstructArgs"
    ) as mock_superuser_construct_args:
        return UserManagementStack(app, args), Mocks(
            mock_user_pool_construct,
            mock_user_pool_construct_args,
            mock_superuser_construct,
            mock_superuser_construct_args,
        )


def test_default_id(
    mocked_user_management_stack: tuple[UserManagementStack, Mocks],
    config: Config,
):
    stack, _ = mocked_user_management_stack
    assert (
        stack.node.id
        == f"{config.project_name}-{config.environment_name}-user-management"
    )


def test_user_pool_construct(
    mocked_user_management_stack: tuple[UserManagementStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_user_management_stack

    mocks.user_pool_construct_args.assert_called_once_with(config)
    mocks.user_pool_construct.assert_called_once_with(
        stack, mocks.user_pool_construct_args.return_value
    )


def test_superuser_construct(
    mocked_user_management_stack: tuple[UserManagementStack, Mocks],
    config: Config,
):
    stack, mocks = mocked_user_management_stack

    mocks.superuser_construct_args.assert_called_once_with(
        config, mocks.user_pool_construct.return_value.user_pool_id
    )
    mocks.superuser_construct.assert_called_once_with(
        stack, mocks.superuser_construct_args.return_value
    )
