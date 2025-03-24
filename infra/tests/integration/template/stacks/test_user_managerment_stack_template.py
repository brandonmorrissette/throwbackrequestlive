# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import assertions

from infra.config import Config
from infra.stacks.user_management import UserManagementStack, UserManagementStackArgs


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config) -> UserManagementStack:
    return UserManagementStack(app, UserManagementStackArgs(config))


def test_user_pool(user_pools: Mapping[str, Any]) -> None:
    assert len(user_pools) == 1


def test_super_user_construct(
    user_groups: Mapping[str, Any],
) -> None:
    assert len(user_groups) == 1
    assert (
        "superuser" in user_groups[next(iter(user_groups))]["Properties"]["GroupName"]
    )


def test_cfn_output(
    template: assertions.Template,
    task_definitions: Mapping[str, Any],
) -> None:
    superuser_task_definition_output = template.find_outputs(
        "superusertaskdefinitionarn"
    )
    assert superuser_task_definition_output
    assert superuser_task_definition_output["superusertaskdefinitionarn"]["Value"][
        "Ref"
    ] == next((key for key in task_definitions.keys()), None)
