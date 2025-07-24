# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import assertions
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.stacks.storage import StorageStack, StorageStackArgs


@pytest.fixture(scope="module")
def app() -> cdk.App:
    return cdk.App()


@pytest.fixture(scope="module")
def config() -> Config:
    return Config(
        "StorageSynthTest",
        "IntegrationTesting",
        cdk.Environment(account="IntegrationTestAccount", region="us-east-1"),
    )


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config, vpc: ec2.Vpc) -> StorageStack:
    return StorageStack(app, StorageStackArgs(config, vpc))


def test_db_instance(db_instances: Mapping[str, Any]) -> None:
    assert len(db_instances) == 1


def test_cache_cluster(cache_clusters: Mapping[str, Any]) -> None:
    assert len(cache_clusters) == 1


def test_cfn_output(
    template: assertions.Template,
    security_groups: Mapping[str, Any],
    task_definitions: Mapping[str, Any],
) -> None:
    security_group_output = template.find_outputs("securitygroupid")
    assert security_group_output
    assert security_group_output["securitygroupid"]["Value"]["Fn::GetAtt"] == [
        next((key for key in security_groups.keys()), None),
        "GroupId",
    ]

    sql_task_definition_output = template.find_outputs("sqltaskdefinitionarn")
    assert sql_task_definition_output["sqltaskdefinitionarn"]["Value"]["Ref"] == next(
        (key for key in task_definitions.keys()), None
    )
