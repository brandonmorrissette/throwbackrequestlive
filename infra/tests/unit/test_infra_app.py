# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
import importlib
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import ANY, MagicMock, call, patch

import pytest

with patch("aws_cdk.App"), patch("aws_cdk.Environment"), patch(
    "infra.config.Config"
) as mock_config, patch("infra.stacks.user_management.UserManagementStack"), patch(
    "infra.stacks.network.NetworkStack"
), patch(
    "infra.stacks.compute.ComputeStack"
), patch(
    "infra.stacks.storage.StorageStack"
), patch(
    "infra.stacks.runtime.RuntimeStack"
), patch(
    "infra.stacks.runtime.RuntimeStackArgs"
):
    from infra import app


def test_default_project_name():
    with patch("aws_cdk.App"), patch("aws_cdk.Environment"), patch(
        "infra.config.Config"
    ) as mock_config, patch("infra.stacks.user_management.UserManagementStack"), patch(
        "infra.stacks.network.NetworkStack"
    ), patch(
        "infra.stacks.compute.ComputeStack"
    ), patch(
        "infra.stacks.storage.StorageStack"
    ), patch(
        "infra.stacks.runtime.RuntimeStack"
    ), patch(
        "infra.stacks.runtime.RuntimeStackArgs"
    ):
        importlib.reload(app)

    assert mock_config.call_args == call(
        # Pointing to project root
        Path(__file__).parent.parent.parent.parent.name,
        ANY,
        ANY,
    )


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring, too-many-instance-attributes, too-many-locals
    cdk_app: MagicMock
    cdk_env: MagicMock
    config: MagicMock
    os_get_env: MagicMock
    user_management_stack: MagicMock
    user_management_stack_args: MagicMock
    network_stack: MagicMock
    network_stack_args: MagicMock
    compute_stack: MagicMock
    compute_stack_args: MagicMock
    storage_stack: MagicMock
    storage_stack_args: MagicMock
    runtime_stack: MagicMock
    runtime_stack_args: MagicMock


@pytest.fixture(scope="module")
def mock_invocations():  # pylint: disable=missing-function-docstring, missing-module-docstring, too-many-locals
    with patch("aws_cdk.App") as mock_cdk_app, patch(
        "aws_cdk.Environment"
    ) as mock_env, patch("infra.config.Config") as mock_config, patch(
        "os.getenv"
    ) as mock_get_env, patch(
        "infra.stacks.user_management.UserManagementStack"
    ) as mock_user_management_stack, patch(
        "infra.stacks.user_management.UserManagementStackArgs"
    ) as mock_user_management_stack_args, patch(
        "infra.stacks.network.NetworkStack"
    ) as mock_network_stack, patch(
        "infra.stacks.network.NetworkStackArgs"
    ) as mock_network_stack_args, patch(
        "infra.stacks.compute.ComputeStack"
    ) as mock_compute_stack, patch(
        "infra.stacks.compute.ComputeStackArgs"
    ) as mock_compute_stack_args, patch(
        "infra.stacks.storage.StorageStack"
    ) as mock_storage_stack, patch(
        "infra.stacks.storage.StorageStackArgs"
    ) as mock_storage_stack_args, patch(
        "infra.stacks.runtime.RuntimeStack"
    ) as mock_runtime_stack, patch(
        "infra.stacks.runtime.RuntimeStackArgs"
    ) as mock_runtime_stack_args:
        importlib.reload(app)

    return Mocks(
        cdk_app=mock_cdk_app,
        cdk_env=mock_env,
        config=mock_config,
        os_get_env=mock_get_env,
        user_management_stack=mock_user_management_stack,
        user_management_stack_args=mock_user_management_stack_args,
        network_stack=mock_network_stack,
        network_stack_args=mock_network_stack_args,
        compute_stack=mock_compute_stack,
        compute_stack_args=mock_compute_stack_args,
        storage_stack=mock_storage_stack,
        storage_stack_args=mock_storage_stack_args,
        runtime_stack=mock_runtime_stack,
        runtime_stack_args=mock_runtime_stack_args,
    )


def test_app_creation(mock_invocations):
    mock_invocations.cdk_app.assert_called_once()


def test_config_instantiated(mock_invocations):
    mock_invocations.config.assert_called_once_with(
        mock_invocations.os_get_env.return_value,
        mock_invocations.os_get_env.return_value,
        mock_invocations.cdk_env.return_value,
    )

    mock_invocations.os_get_env.assert_has_calls(
        [
            call("PROJECT_NAME", Path(__file__).parent.parent.parent.parent.name),
            call("ENVIRONMENT_NAME"),
            call("AWS_ACCOUNT"),
            call("AWS_REGION"),
        ]
    )

    mock_invocations.cdk_env.assert_called_once_with(
        account=mock_invocations.os_get_env.return_value,
        region=mock_invocations.os_get_env.return_value,
    )


def test_user_management_stack(mock_invocations):
    mock_invocations.user_management_stack_args.assert_called_once_with(
        mock_invocations.config.return_value
    )
    mock_invocations.user_management_stack.assert_called_once_with(
        mock_invocations.cdk_app.return_value,
        mock_invocations.user_management_stack_args.return_value,
    )


def test_network_stack(mock_invocations):
    mock_invocations.network_stack_args.assert_called_once_with(
        mock_invocations.config.return_value
    )

    mock_invocations.network_stack.assert_called_once_with(
        mock_invocations.cdk_app.return_value,
        mock_invocations.network_stack_args.return_value,
    )


def test_compute_stack(mock_invocations):
    mock_invocations.compute_stack_args.assert_called_once_with(
        mock_invocations.config.return_value,
        vpc=mock_invocations.network_stack.return_value.vpc_construct.vpc,
    )
    mock_invocations.compute_stack.assert_called_once_with(
        mock_invocations.cdk_app.return_value,
        mock_invocations.compute_stack_args.return_value,
    )
    mock_invocations.compute_stack.return_value.add_dependency.assert_called_once_with(
        mock_invocations.network_stack.return_value
    )


def test_storage_stack(mock_invocations):
    mock_invocations.storage_stack_args.assert_called_once_with(
        mock_invocations.config.return_value,
        vpc=mock_invocations.network_stack.return_value.vpc_construct.vpc,
    )
    mock_invocations.storage_stack.assert_called_once_with(
        mock_invocations.cdk_app.return_value,
        mock_invocations.storage_stack_args.return_value,
    )
    mock_invocations.storage_stack.return_value.add_dependency.assert_called_once_with(
        mock_invocations.network_stack.return_value
    )


def test_runtime_stack(mock_invocations):
    mock_invocations.runtime_stack_args.assert_called_once_with(
        mock_invocations.config.return_value,
        mock_invocations.user_management_stack.return_value,
        mock_invocations.network_stack.return_value,
        mock_invocations.compute_stack.return_value,
        mock_invocations.storage_stack.return_value,
    )
    mock_invocations.runtime_stack.assert_called_once_with(
        mock_invocations.cdk_app.return_value,
        mock_invocations.runtime_stack_args.return_value,
    )
    mock_invocations.runtime_stack.return_value.add_dependency.assert_has_calls(
        [
            call(mock_invocations.user_management_stack.return_value),
            call(mock_invocations.network_stack.return_value),
            call(mock_invocations.compute_stack.return_value),
            call(mock_invocations.storage_stack.return_value),
        ]
    )


def test_app_synth(mock_invocations):
    mock_invocations.cdk_app.return_value.synth.assert_called_once()
