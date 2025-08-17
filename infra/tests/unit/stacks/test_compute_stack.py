# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.stacks.compute import ComputeStack, ComputeStackArgs


@pytest.fixture(scope="module")
def compute_stack_args(config: Config, vpc: MagicMock):
    return ComputeStackArgs(config, vpc)


@pytest.fixture(scope="module")
def mocked_compute_stack(
    app: cdk.App, compute_stack_args: ComputeStackArgs
) -> tuple[ComputeStack, MagicMock, MagicMock]:
    with patch(
        "infra.stacks.compute.ClusterConstruct"
    ) as mock_cluster_construct, patch(
        "infra.stacks.compute.ClusterConstructArgs"
    ) as mock_cluster_construct_args:
        return (
            ComputeStack(app, compute_stack_args),
            mock_cluster_construct,
            mock_cluster_construct_args,
        )


def test_default_id(
    mocked_compute_stack: tuple[ComputeStack, MagicMock, MagicMock],
    config: Config,
):
    (
        stack,
        _,
        _,
    ) = mocked_compute_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-compute"


def test_cluster_construct(
    mocked_compute_stack: tuple[ComputeStack, MagicMock, MagicMock],
    compute_stack_args: ComputeStackArgs,
):
    stack, mock_cluster_construct, mock_cluster_construct_args = mocked_compute_stack

    mock_cluster_construct_args.assert_called_once_with(
        compute_stack_args.config, compute_stack_args.vpc
    )
    mock_cluster_construct.assert_called_once_with(
        stack, mock_cluster_construct_args.return_value
    )
