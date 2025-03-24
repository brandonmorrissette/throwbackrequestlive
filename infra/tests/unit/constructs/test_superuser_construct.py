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


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    iam: MagicMock
    user_pool_group: MagicMock
    ecs: MagicMock
    ecs_patterns: MagicMock
    logs: MagicMock


@pytest.fixture(scope="module")
def mock_superuser_construct(config: Config, stack: Stack, user_pool_id: str):
    with patch("infra.constructs.superuser.iam") as mock_iam, patch(
        "infra.constructs.superuser.CfnUserPoolGroup"
    ) as mock_user_pool_group, patch(
        "infra.constructs.superuser.ecs"
    ) as mock_ecs, patch(
        "infra.constructs.superuser.logs"
    ) as mock_logs:
        yield SuperUserConstruct(
            stack, SuperUserConstructArgs(config, user_pool_id)
        ), Mocks(
            iam=mock_iam,
            user_pool_group=mock_user_pool_group,
            ecs=mock_ecs,
            ecs_patterns=MagicMock(),
            logs=mock_logs,
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
    config: Config,
    user_pool_id: str,
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
    assert set(mocks.iam.PolicyStatement.call_args[1]["actions"]) == set(
        expected_actions
    )
    assert mocks.iam.PolicyStatement.call_args[1]["resources"] == [
        f"arn:aws:cognito-idp:{config.cdk_environment.region}:"
        f"{config.cdk_environment.account}:userpool/{user_pool_id}"
    ]


def test_role_creation(mock_superuser_construct: tuple[SuperUserConstruct, Mocks]):
    construct, mocks = mock_superuser_construct

    mocks.iam.Role.assert_called_once_with(
        construct,
        ANY,
        role_name=ANY,
        assumed_by=mocks.iam.ServicePrincipal.return_value,
        managed_policies=[mocks.iam.ManagedPolicy.return_value],
    )

    mocks.iam.ServicePrincipal.assert_called_once_with("cognito-idp.amazonaws.com")


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


def test_task_definition_creation(
    mock_superuser_construct: tuple[SuperUserConstruct, Mocks],
):
    construct, mocks = mock_superuser_construct

    mocks.ecs.FargateTaskDefinition.assert_called_once_with(
        construct,
        "superuser-task-definition",
        memory_limit_mib=512,
        cpu=256,
        task_role=mocks.iam.Role.return_value,
    )


def test_container_added(mock_superuser_construct: tuple[SuperUserConstruct, Mocks]):
    _, mocks = mock_superuser_construct

    mocks.ecs.FargateTaskDefinition.return_value.add_container.assert_called_once_with(
        ANY,
        image=mocks.ecs.ContainerImage.from_asset.return_value,
        logging=mocks.ecs.LogDrivers.aws_logs.return_value,
    )

    mocks.ecs.ContainerImage.from_asset.assert_called_once_with(
        "infra/setup/create_superuser"
    )


def test_logging(
    mock_superuser_construct: tuple[SuperUserConstruct, Mocks], config: Config
):
    construct, mocks = mock_superuser_construct

    mocks.ecs.LogDrivers.aws_logs.assert_called_once_with(
        stream_prefix="superuser-creation",
        log_group=mocks.logs.LogGroup.return_value,
    )

    mocks.logs.LogGroup.assert_called_once_with(
        construct,
        "superuser-container-log-group",
        log_group_name=f"{config.project_name}-superuser-container-logs",
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )
