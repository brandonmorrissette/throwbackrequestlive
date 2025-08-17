# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import ANY, MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.superuser import SuperUserConstruct, SuperUserConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def user_pool_id():
    return "test-user-pool-id"


@pytest.fixture(scope="module")
def user_pool_resource_arn(config: Config, user_pool_id: str):
    return f"arn:aws:cognito-idp:{config.cdk_environment.region}:{config.cdk_environment.account}:userpool/{user_pool_id}"  # pylint: disable=line-too-long


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    iam: MagicMock
    user_pool_group: MagicMock


@pytest.fixture(scope="module")
def mock_superuser_construct(config: Config, stack: Stack, user_pool_id: str):
    with patch("infra.constructs.superuser.iam") as mock_iam, patch(
        "infra.constructs.superuser.CfnUserPoolGroup"
    ) as mock_user_pool_group:
        yield SuperUserConstruct(
            stack, SuperUserConstructArgs(config, user_pool_id)
        ), Mocks(
            iam=mock_iam,
            user_pool_group=mock_user_pool_group,
        )


def test_construct_inheritance():
    assert issubclass(SuperUserConstruct, Construct)


def test_default_id(
    mock_superuser_construct: tuple[SuperUserConstruct, Mocks], config: Config
):
    construct, _ = mock_superuser_construct
    assert (
        construct.node.id
        == f"{config.project_name}-{config.environment_name}-superuser"
    )


def test_policy_creation(
    mock_superuser_construct: tuple[SuperUserConstruct, Mocks],
    user_pool_resource_arn: str,
):
    construct, mocks = mock_superuser_construct

    # pylint: disable=R0801
    mocks.iam.ManagedPolicy.assert_called_once_with(
        construct,
        ANY,
        managed_policy_name=ANY,
        statements=[
            mocks.iam.PolicyStatement.return_value,
        ],
    )
    # pylint: disable=R0801
    expected_actions = [
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminDeleteUser",
        "cognito-idp:AdminUpdateUserAttributes",
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:AdminRemoveUserFromGroup",
        "cognito-idp:AdminCreateGroup",
        "cognito-idp:AdminDeleteGroup",
        "cognito-idp:AdminUpdateGroup",
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:ListUsers",
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:ListUserPools",
    ]
    assert set(
        mocks.iam.PolicyStatement.call_args_list[0].kwargs.get("actions")
    ) == set(expected_actions)
    assert mocks.iam.PolicyStatement.call_args_list[0].kwargs.get("resources") == [
        user_pool_resource_arn
    ]


def test_role_creation(mock_superuser_construct: tuple[SuperUserConstruct, Mocks]):
    construct, mocks = mock_superuser_construct

    mocks.iam.Role.assert_any_call(
        construct,
        ANY,
        role_name=ANY,
        assumed_by=mocks.iam.ServicePrincipal.return_value,
        managed_policies=[mocks.iam.ManagedPolicy.return_value],
    )

    mocks.iam.ServicePrincipal.assert_any_call("cognito-idp.amazonaws.com")


def test_user_pool_group_creation(
    mock_superuser_construct: tuple[SuperUserConstruct, Mocks], user_pool_id: str
):
    construct, mocks = mock_superuser_construct

    mocks.user_pool_group.assert_called_once_with(
        construct,
        ANY,
        group_name="superuser",
        user_pool_id=user_pool_id,
        description="Superuser group with elevated permissions",
        role_arn=mocks.iam.Role.return_value.role_arn,
    )
