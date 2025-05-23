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


# pylint: disable=R0801
def test_task_role(
    task_role: Mapping[str, Any], managed_policies: Mapping[str, Any]
) -> None:
    assert task_role
    assert task_role["Properties"]["AssumeRolePolicyDocument"]["Statement"] == [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
        }
    ]
    assert task_role["Properties"]["ManagedPolicyArns"] == [
        {"Ref": next(iter(managed_policies.keys()))}
    ]


def test_task_definition(
    task_definitions: Mapping[str, Any],
    roles: Mapping[str, Any],
    task_role: Mapping[str, Any],
) -> None:
    task_definition = next(iter(task_definitions.values()))

    assert task_definition["Properties"]["RequiresCompatibilities"] == ["FARGATE"]
    assert task_definition["Properties"]["TaskRoleArn"]["Fn::GetAtt"] == [
        next(key for key, value in roles.items() if value == task_role),
        "Arn",
    ]


def test_container_definition(
    task_definitions: Mapping[str, Any],
    log_groups: Mapping[str, Any],
) -> None:
    task_definition = next(iter(task_definitions.values()))

    container_definition = next(
        iter(task_definition["Properties"]["ContainerDefinitions"])
    )

    assert container_definition["Name"] == "superuser-container"
    logging_options = container_definition["LogConfiguration"]["Options"]
    assert logging_options["awslogs-group"] == {"Ref": next(iter(log_groups.keys()))}
    assert logging_options["awslogs-stream-prefix"] == "superuser-creation"
