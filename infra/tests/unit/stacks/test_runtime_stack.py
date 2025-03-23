# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs


@pytest.fixture(scope="module")
def mock_user_management_stack():
    user_management_stack = MagicMock()
    user_management_stack.superuser_construct.policy = "superuser_policy"
    return user_management_stack


@pytest.fixture(scope="module")
def mock_network_stack():
    network_stack = MagicMock()
    network_stack.cert_construct.certificate = "certificate"
    return network_stack


@pytest.fixture(scope="module")
def mock_compute_stack():
    compute_stack = MagicMock()
    compute_stack.cluster_construct.cluster = "ecs_cluster"
    return compute_stack


@pytest.fixture(scope="module")
def mock_storage_stack():
    storage_stack = MagicMock()
    storage_stack.cache_construct.cluster.attr_redis_endpoint_address = "redis_address"
    storage_stack.cache_construct.cluster.attr_redis_endpoint_port = "redis_port"
    storage_stack.rds_construct.db_instance.secret = "db_instance_secret"
    return storage_stack


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    runtime_construct: MagicMock
    runtime_construct_args: MagicMock
    route53_construct: MagicMock
    route53_construct_args: MagicMock
    ssm: MagicMock
    ecs: MagicMock


@pytest.fixture(scope="module")
def mocked_runtime_stack(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    app: cdk.App,
    config: Config,
    mock_user_management_stack,
    mock_network_stack,
    mock_compute_stack,
    mock_storage_stack,
):
    with patch(
        "infra.stacks.runtime.RuntimeConstruct"
    ) as mock_runtime_construct, patch(
        "infra.stacks.runtime.RuntimeConstructArgs"
    ) as mock_runtime_construct_args, patch(
        "infra.stacks.runtime.Route53Construct"
    ) as mock_route53_construct, patch(
        "infra.stacks.runtime.Route53ConstructArgs"
    ) as mock_route53_construct_args, patch(
        "infra.stacks.runtime.ssm"
    ) as mock_ssm, patch(
        "infra.stacks.runtime.ecs"
    ) as mock_ecs:
        args = RuntimeStackArgs(
            config,
            user_management_stack=mock_user_management_stack,
            network_stack=mock_network_stack,
            compute_stack=mock_compute_stack,
            storage_stack=mock_storage_stack,
        )
        yield RuntimeStack(app, args), Mocks(
            mock_runtime_construct,
            mock_runtime_construct_args,
            mock_route53_construct,
            mock_route53_construct_args,
            mock_ssm,
            mock_ecs,
        )


def test_default_id(
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    config: Config,
):
    stack, _ = mocked_runtime_stack
    assert stack.node.id == f"{config.project_name}-{config.environment_name}-runtime"


def test_runtime_construct(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    mock_network_stack: MagicMock,
    mock_user_management_stack: MagicMock,
    mock_compute_stack: MagicMock,
    mock_storage_stack: MagicMock,
    config: Config,
):
    stack, mocks = mocked_runtime_stack

    mocks.runtime_construct.assert_called_once_with(
        stack,
        mocks.runtime_construct_args.return_value,
    )

    mocks.runtime_construct_args.assert_called_once_with(
        config=config,
        certificate=mock_network_stack.cert_construct.certificate,
        policy=mock_user_management_stack.superuser_construct.policy,
        cluster=mock_compute_stack.cluster_construct.cluster,
        runtime_variables={
            "COGNITO_APP_CLIENT_ID": mocks.ssm.StringParameter.value_for_string_parameter.return_value,  # pylint: disable=line-too-long
            "COGNITO_USER_POOL_ID": mocks.ssm.StringParameter.value_for_string_parameter.return_value,  # pylint: disable=line-too-long
            "DB_NAME": config.project_name,
            "REDIS_HOST": mock_storage_stack.cache_construct.cluster.attr_redis_endpoint_address,  # pylint: disable=line-too-long
            "REDIS_PORT": mock_storage_stack.cache_construct.cluster.attr_redis_endpoint_port,
        },
        runtime_secrets={
            "DB_USER": mocks.ecs.Secret.from_secrets_manager.return_value,
            "DB_PASSWORD": mocks.ecs.Secret.from_secrets_manager.return_value,
            "DB_HOST": mocks.ecs.Secret.from_secrets_manager.return_value,
        },
    )

    mocks.ssm.StringParameter.value_for_string_parameter.assert_any_call(
        stack, f"/{config.project_name}/user-pool-client-id"
    )
    mocks.ssm.StringParameter.value_for_string_parameter.assert_any_call(
        stack, f"/{config.project_name}/user-pool-id"
    )

    mocks.ecs.Secret.from_secrets_manager.assert_any_call(
        mock_storage_stack.rds_construct.db_instance.secret, "username"
    )
    mocks.ecs.Secret.from_secrets_manager.assert_any_call(
        mock_storage_stack.rds_construct.db_instance.secret, "password"
    )
    mocks.ecs.Secret.from_secrets_manager.assert_any_call(
        mock_storage_stack.rds_construct.db_instance.secret, "host"
    )


def test_route53_construct(
    mocked_runtime_stack: tuple[RuntimeStack, Mocks],
    mock_network_stack: MagicMock,
    config: Config,
):
    stack, mocks = mocked_runtime_stack

    mocks.route53_construct.assert_called_once_with(
        stack,
        mocks.route53_construct_args.return_value,
    )

    mocks.route53_construct_args.assert_called_once_with(
        config,
        hosted_zone=mock_network_stack.cert_construct.hosted_zone,
        load_balancer=mocks.runtime_construct.return_value.runtime_service.load_balancer,  # pylint: disable=line-too-long
    )
