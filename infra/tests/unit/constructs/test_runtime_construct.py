# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import ANY, MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.runtime import RuntimeConstruct, RuntimeConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def runtime_construct_args(config: Config) -> RuntimeConstructArgs:
    return RuntimeConstructArgs(
        config=config,
        vpc=MagicMock(),
        certificate=MagicMock(),
        policy=MagicMock(),
        cluster=MagicMock(),
        load_balancer=MagicMock(),
        db_instance=MagicMock(),
        runtime_variables=MagicMock(),
    )


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    secretsmanager: MagicMock
    iam: MagicMock
    ecs: MagicMock
    ecs_patterns: MagicMock
    logs: MagicMock
    duration: MagicMock
    ecr_assets: MagicMock
    ec2: MagicMock
    elbv2: MagicMock


@pytest.fixture(scope="module")
def mock_runtime_construct(stack: Stack, runtime_construct_args: MagicMock):
    with patch("infra.constructs.runtime.secretsmanager") as mock_secretsmanager, patch(
        "infra.constructs.runtime.iam"
    ) as mock_iam, patch("infra.constructs.runtime.ecs") as mock_ecs, patch(
        "infra.constructs.runtime.ecs_patterns"
    ) as mock_ecs_patterns, patch(
        "infra.constructs.runtime.aws_logs"
    ) as mock_logs, patch(
        "infra.constructs.runtime.Duration"
    ) as mock_duration, patch(
        "infra.constructs.runtime.ecr_assets"
    ) as mock_ecr_assets, patch(
        "infra.constructs.runtime.ec2"
    ) as mock_ec2, patch(
        "infra.constructs.runtime.elbv2"
    ) as mock_elbv2:

        yield RuntimeConstruct(stack, runtime_construct_args), Mocks(
            mock_secretsmanager,
            mock_iam,
            mock_ecs,
            mock_ecs_patterns,
            mock_logs,
            mock_duration,
            mock_ecr_assets,
            mock_ec2,
            mock_elbv2,
        )


def test_construct_inheritance():
    assert issubclass(RuntimeConstruct, Construct)


def test_default_id(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks], config: Config
):
    construct, _ = mock_runtime_construct
    assert (
        construct.node.id == f"{config.project_name}-{config.environment_name}-runtime"
    )


def test_jwt_secret_creation(mock_runtime_construct: tuple[RuntimeConstruct, Mocks]):
    construct, mocks = mock_runtime_construct

    mocks.secretsmanager.Secret.assert_called_once_with(
        construct,
        ANY,
        description=ANY,
        generate_secret_string=ANY,
    )

    mocks.secretsmanager.SecretStringGenerator.assert_called_once_with(
        password_length=32, exclude_punctuation=True
    )

    mocks.ecs.Secret.from_secrets_manager.assert_called_once_with(
        mocks.secretsmanager.Secret.return_value
    )


def test_policy_created(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks],
    runtime_construct_args: RuntimeConstructArgs,
    config: Config,
):
    construct, mocks = mock_runtime_construct

    mocks.iam.ManagedPolicy.assert_called_once_with(
        construct,
        ANY,
        managed_policy_name=ANY,
        statements=[
            mocks.iam.PolicyStatement.return_value,
            mocks.iam.PolicyStatement.return_value,
            mocks.iam.PolicyStatement.return_value,
        ],
    )
    mocks.iam.PolicyStatement.assert_any_call(
        actions=["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
        resources=[
            mocks.secretsmanager.Secret.return_value.secret_arn,
            runtime_construct_args.db_instance.secret.secret_arn,
        ],
    )
    mocks.iam.PolicyStatement.assert_any_call(
        actions=["ssm:GetParameter"],
        resources=[
            f"arn:aws:ssm:{config.cdk_environment.region}:"
            f"{config.cdk_environment.account}:parameter/{config.project_name}-{config.environment_name}/*"  # pylint: disable=line-too-long
        ],
    )

    mocks.iam.PolicyStatement.assert_any_call(
        actions=[
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject",
        ],
        resources=[
            f"arn:aws:s3:::{config.project_name}-"
            f"{config.environment_name}-bucket/*",
        ],
    )


def test_task_role_creation(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks],
    runtime_construct_args: MagicMock,
):
    construct, mocks = mock_runtime_construct

    # pylint: disable=R0801
    mocks.iam.Role.assert_called_once_with(
        construct,
        ANY,
        role_name=ANY,
        assumed_by=mocks.iam.ServicePrincipal.return_value,
        managed_policies=[
            mocks.iam.ManagedPolicy.from_aws_managed_policy_name.return_value,
            runtime_construct_args.policy,
            mocks.iam.ManagedPolicy.return_value,
        ],
    )

    mocks.iam.ServicePrincipal.assert_any_call("ecs-tasks.amazonaws.com")
    mocks.iam.ManagedPolicy.from_aws_managed_policy_name.assert_called_once_with(
        "service-role/AmazonECSTaskExecutionRolePolicy"
    )


def test_docker_image_creation(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks], config: Config
):
    construct, mocks = mock_runtime_construct

    mocks.ecr_assets.DockerImageAsset.assert_called_once_with(
        construct,
        f"{config.project_name}-{config.environment_name}-image",
        directory=".",
        exclude=["infra", "infra/*", "cdk.out", "node_modules"],
    )


def test_task_image_creation(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks],
    runtime_construct_args: MagicMock,
):
    _, mocks = mock_runtime_construct

    mocks.ecs.ContainerImage.from_docker_image_asset.assert_called_once_with(
        mocks.ecr_assets.DockerImageAsset.return_value
    )

    mocks.ecs_patterns.ApplicationLoadBalancedTaskImageOptions.assert_called_once_with(
        image=mocks.ecs.ContainerImage.from_docker_image_asset.return_value,
        container_port=5000,
        log_driver=mocks.ecs.LogDrivers.aws_logs.return_value,
        environment=runtime_construct_args.runtime_variables,
        secrets={"JWT_SECRET_KEY": mocks.ecs.Secret.from_secrets_manager.return_value},
        task_role=mocks.iam.Role.return_value,
    )


def test_runtime_service_creation(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks],
    runtime_construct_args: MagicMock,
    load_balancer,
):
    construct, mocks = mock_runtime_construct

    mocks.ecs_patterns.ApplicationLoadBalancedFargateService.assert_called_once_with(
        construct,
        "runtime-service",
        cluster=runtime_construct_args.cluster,
        desired_count=1,
        task_image_options=mocks.ecs_patterns.ApplicationLoadBalancedTaskImageOptions.return_value,
        certificate=runtime_construct_args.certificate,
        redirect_http=True,
        health_check_grace_period=mocks.duration.minutes.return_value,
        load_balancer=runtime_construct_args.load_balancer,
        ip_address_type=mocks.elbv2.IpAddressType.IPV4,
        security_groups=[mocks.ec2.SecurityGroup.return_value],
        assign_public_ip=True,
    )


def test_logging_configuration(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks], config: Config
):
    construct, mocks = mock_runtime_construct

    mocks.ecs.LogDrivers.aws_logs.assert_called_once_with(
        stream_prefix=config.project_name,
        log_group=mocks.logs.LogGroup.return_value,
    )
    mocks.logs.LogGroup.assert_called_once_with(
        construct,
        ANY,
        log_group_name=f"/{config.project_name}-{config.environment_name}-runtime",
        retention=mocks.logs.RetentionDays.ONE_WEEK,
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )


def test_health_check_configuration(
    mock_runtime_construct: tuple[RuntimeConstruct, Mocks],
):
    construct, mocks = mock_runtime_construct

    construct.runtime_service.target_group.configure_health_check.assert_called_once_with(
        path="/",
        interval=mocks.duration.seconds.return_value,
        timeout=mocks.duration.seconds.return_value,
        healthy_http_codes="200",
    )

    mocks.duration.seconds.assert_any_call(30)
    mocks.duration.seconds.assert_any_call(10)
