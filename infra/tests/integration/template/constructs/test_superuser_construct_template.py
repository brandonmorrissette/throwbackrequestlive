# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest

from infra.config import Config
from infra.constructs import superuser
from infra.constructs.superuser import SuperUserConstruct, SuperUserConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config) -> SuperUserConstruct:
    return SuperUserConstruct(
        stack,
        SuperUserConstructArgs(config=config, user_pool_id="test-user-pool-id"),
    )


@pytest.fixture(scope="module")
def role(roles: Mapping[str, Any], config: Config) -> Any | None:
    return next(
        (
            role
            for role in roles.values()
            if role["Properties"].get("RoleName")
            == f"{config.project_name}-{config.environment_name}-superuser-role"
        ),
        None,
    )


@pytest.fixture(scope="module")
def task_role(roles: Mapping[str, Any], config: Config) -> Any | None:
    return next(
        (
            role
            for role in roles.values()
            if role["Properties"].get("RoleName")
            == f"{config.project_name}-{config.environment_name}-superuser-task-role"
        ),
        None,
    )


def test_policy(managed_policies: Mapping[str, Any], config: Config) -> None:
    policy = next(
        (
            policy
            for policy in managed_policies.values()
            if policy["Properties"].get("ManagedPolicyName")
            == f"{config.project_name}-{config.environment_name}-cognito-policy"
        ),
        None,
    )

    assert policy
    assert any(
        statement["Action"] == superuser.PERMITTED_ACTIONS
        for statement in policy["Properties"]["PolicyDocument"]["Statement"]
    )


def test_role(role: Mapping[str, Any], managed_policies: Mapping[str, Any]) -> None:
    assert role
    assert role["Properties"]["AssumeRolePolicyDocument"]["Statement"] == [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {"Service": "cognito-idp.amazonaws.com"},
        }
    ]
    assert role["Properties"]["ManagedPolicyArns"] == [
        {"Ref": next(iter(managed_policies.keys()))}
    ]


def test_user_pool_group(user_pool_groups: Mapping[str, Any]) -> None:
    user_pool_group = next(iter(user_pool_groups.values()))

    assert user_pool_group["Properties"]["GroupName"] == "superuser"
    assert (
        user_pool_group["Properties"]["Description"]
        == "Superuser group with elevated permissions"
    )
