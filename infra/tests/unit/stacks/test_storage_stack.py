# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.stacks.storage import StorageStack, StorageStackArgs


@pytest.fixture(scope="module")
def args(config: Config, vpc: ec2.IVpc) -> StorageStackArgs:
    return StorageStackArgs(
        config=config,
        vpc=vpc,
    )


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    rds_construct: MagicMock
    rds_construct_args: MagicMock
    cache_construct: MagicMock
    cache_construct_args: MagicMock
    cfn_output: MagicMock


@pytest.fixture(scope="module")
def mocked_storage_stack(
    app: cdk.App, args: StorageStackArgs
) -> tuple[StorageStack, Mocks]:
    with patch("infra.stacks.storage.RdsConstruct") as mock_rds_construct, patch(
        "infra.stacks.storage.RdsConstructArgs"
    ) as mock_rds_construct_args, patch(
        "infra.stacks.storage.CacheConstruct"
    ) as mock_cache_construct, patch(
        "infra.stacks.storage.CacheConstructArgs"
    ) as mock_cache_construct_args, patch(
        "infra.stacks.storage.CfnOutput"
    ) as mock_cfn_output:
        return StorageStack(app, args), Mocks(
            rds_construct=mock_rds_construct,
            rds_construct_args=mock_rds_construct_args,
            cache_construct=mock_cache_construct,
            cache_construct_args=mock_cache_construct_args,
            cfn_output=mock_cfn_output,
        )


def test_default_id(
    mocked_storage_stack: tuple[StorageStack, Mocks],
    config: Config,
):
    stack, _ = mocked_storage_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-storage"


def test_rds_construct(
    mocked_storage_stack: tuple[StorageStack, Mocks],
    vpc: MagicMock,
    config: Config,
):
    stack, mocks = mocked_storage_stack

    mocks.rds_construct_args.assert_called_once_with(config, vpc)
    mocks.rds_construct.assert_called_once_with(
        stack, mocks.rds_construct_args.return_value
    )


def test_cache_construct(
    mocked_storage_stack: tuple[StorageStack, Mocks],
    vpc: MagicMock,
    config: Config,
):
    stack, mocks = mocked_storage_stack

    mocks.cache_construct_args.assert_called_once_with(config, vpc)
    mocks.cache_construct.assert_called_once_with(
        stack, mocks.cache_construct_args.return_value
    )


def test_cfn_output(
    mocked_storage_stack: tuple[StorageStack, Mocks],
):
    stack, mocks = mocked_storage_stack

    mocks.cfn_output.assert_any_call(
        stack,
        "securitygroupid",
        value=mocks.rds_construct.return_value.security_group.security_group_id,
    )

    mocks.cfn_output.assert_any_call(
        stack,
        "sqltaskdefinitionarn",
        value=mocks.rds_construct.return_value.task_definition.task_definition_arn,
    )
