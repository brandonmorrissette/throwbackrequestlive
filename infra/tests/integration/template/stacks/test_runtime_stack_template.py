# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
import aws_cdk as cdk
import pytest
from aws_cdk import assertions

from infra.config import Config
from infra.stacks.compute import ComputeStack, ComputeStackArgs
from infra.stacks.network import NetworkStack, NetworkStackArgs
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs
from infra.stacks.storage import StorageStack, StorageStackArgs
from infra.stacks.user_management import UserManagementStack, UserManagementStackArgs


@pytest.fixture(scope="module")
def network_stack(app: cdk.App, config: Config) -> NetworkStack:
    return NetworkStack(app, NetworkStackArgs(config))


@pytest.fixture(scope="module")
def compute_stack(
    app: cdk.App, config: Config, network_stack: NetworkStack
) -> ComputeStack:
    return ComputeStack(app, ComputeStackArgs(config, network_stack.vpc_constrcut.vpc))


@pytest.fixture(scope="module")
def storage_stack(
    app: cdk.App, config: Config, network_stack: NetworkStack
) -> StorageStack:
    return StorageStack(app, StorageStackArgs(config, network_stack.vpc_constrcut.vpc))


@pytest.fixture(scope="module")
def user_management_stack(app: cdk.App, config: Config) -> UserManagementStack:
    return UserManagementStack(app, UserManagementStackArgs(config))


@pytest.fixture(scope="module")
def stack(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    app: cdk.App,
    config: Config,
    network_stack: NetworkStack,
    compute_stack: ComputeStack,
    storage_stack: StorageStack,
    user_management_stack: UserManagementStack,
) -> RuntimeStack:
    return RuntimeStack(
        app,
        RuntimeStackArgs(
            config,
            user_management_stack=user_management_stack,
            network_stack=network_stack,
            compute_stack=compute_stack,
            storage_stack=storage_stack,
        ),
    )


def test_runtime_service_resources(template: assertions.Template) -> None:
    resources = template.find_resources("AWS::ECS::Service")
    assert len(resources) == 1


def test_route53_resources(template: assertions.Template) -> None:
    resources = template.find_resources("AWS::Route53::RecordSet")
    assert len(resources) == 2
