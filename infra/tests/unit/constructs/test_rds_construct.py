# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import ANY, MagicMock, patch

import aws_cdk as cdk
import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.rds import RdsConstruct, RdsConstructArgs
from infra.stacks.stack import Stack


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    ec2: MagicMock
    rds: MagicMock
    iam: MagicMock
    ecs: MagicMock
    logs: MagicMock
    duration: MagicMock


@pytest.fixture(scope="module")
def mock_rds_construct(vpc: ec2.Vpc, config: Config, stack: Stack):
    with patch("infra.constructs.rds.ec2") as mock_ec2, patch(
        "infra.constructs.rds.rds"
    ) as mock_rds, patch("infra.constructs.rds.iam") as mock_iam, patch(
        "infra.constructs.rds.ecs"
    ) as mock_ecs, patch(
        "infra.constructs.rds.logs"
    ) as mock_logs, patch(
        "infra.constructs.rds.Duration"
    ) as mock_duration:

        yield RdsConstruct(stack, RdsConstructArgs(config, vpc)), Mocks(
            mock_ec2, mock_rds, mock_iam, mock_ecs, mock_logs, mock_duration
        )


def test_construct_inheritance():
    assert issubclass(RdsConstruct, Construct)


def test_default_id(mock_rds_construct: tuple[RdsConstruct, Mocks], config: Config):
    construct, _ = mock_rds_construct
    assert construct.node.id == f"{config.project_name}-{config.environment_name}-rds"


def test_security_group_creation(
    mock_rds_construct: tuple[RdsConstruct, Mocks], vpc: ec2.Vpc
):
    construct, mocks = mock_rds_construct

    mocks.ec2.SecurityGroup.assert_called_once_with(construct, ANY, vpc=vpc)

    mocks.ec2.SecurityGroup.return_value.add_ingress_rule.assert_called_once_with(
        mocks.ec2.Peer.ipv4(vpc.vpc_cidr_block),
        mocks.ec2.Port.tcp(5432),
        ANY,
    )


def test_db_instance_creation(
    mock_rds_construct: tuple[RdsConstruct, Mocks], config: Config, vpc: ec2.Vpc
):
    construct, mocks = mock_rds_construct

    mocks.rds.DatabaseInstance.assert_called_once_with(
        construct,
        ANY,
        database_name=config.project_name,
        engine=ANY,
        instance_type=ANY,
        vpc=vpc,
        credentials=ANY,
        allocated_storage=ANY,
        multi_az=ANY,
        publicly_accessible=False,
        backup_retention=mocks.duration.days(7),
        security_groups=[mocks.ec2.SecurityGroup.return_value],
        instance_identifier=ANY,
    )

    mocks.rds.Credentials.from_generated_secret.assert_called_once_with(
        "db_master_user",
        secret_name=f"{config.project_name}-db-credentials",
    )


def test_policy_creation(mock_rds_construct: tuple[RdsConstruct, Mocks]):
    construct, mocks = mock_rds_construct

    mocks.iam.ManagedPolicy.assert_called_once_with(
        construct,
        ANY,
        managed_policy_name=ANY,
        statements=[
            mocks.iam.PolicyStatement.return_value,
            mocks.iam.PolicyStatement.return_value,
        ],
    )

    mocks.iam.PolicyStatement.assert_any_call(
        actions=[
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
        ],
        resources=[mocks.rds.DatabaseInstance.return_value.secret.secret_arn],
    )

    mocks.iam.PolicyStatement.assert_any_call(
        actions=["rds-db:connect"],
        resources=[mocks.rds.DatabaseInstance.return_value.instance_arn],
    )


def test_task_role_creation(mock_rds_construct: tuple[RdsConstruct, Mocks]):
    construct, mocks = mock_rds_construct

    mocks.iam.ServicePrincipal.assert_any_call("ecs-tasks.amazonaws.com")

    # pylint: disable=R0801
    mocks.iam.Role.assert_called_once_with(
        construct,
        ANY,
        role_name=ANY,
        assumed_by=mocks.iam.ServicePrincipal.return_value,
        managed_policies=[mocks.iam.ManagedPolicy.return_value],
    )


def test_task_definition_creation(mock_rds_construct: tuple[RdsConstruct, Mocks]):
    construct, mocks = mock_rds_construct

    mocks.ecs.FargateTaskDefinition.assert_called_with(
        construct,
        ANY,
        memory_limit_mib=ANY,
        cpu=ANY,
        task_role=mocks.iam.Role.return_value,
    )


def test_container_added(mock_rds_construct: tuple[RdsConstruct, Mocks]):
    construct, mocks = mock_rds_construct

    mocks.ecs.FargateTaskDefinition.return_value.add_container.assert_called_once_with(
        ANY,
        image=ANY,
        command=ANY,
        logging=ANY,
        secrets={
            "DB_USER": mocks.ecs.Secret.from_secrets_manager.return_value,
            "DB_PASSWORD": mocks.ecs.Secret.from_secrets_manager.return_value,
        },
        environment={"DB_HOST": construct.db_instance.db_instance_endpoint_address},
    )

    mocks.ecs.LogDrivers.aws_logs.assert_called_once_with(
        stream_prefix=ANY,
        log_group=ANY,
    )

    mocks.logs.LogGroup.assert_called_once_with(
        construct,
        ANY,
        log_group_name=ANY,
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )

    mocks.ecs.ContainerImage.from_asset.assert_called_once_with(
        "infra", file="setup/deploy_sql/Dockerfile"
    )

    mocks.ecs.Secret.from_secrets_manager.assert_any_call(
        mocks.rds.DatabaseInstance.return_value.secret, field="username"
    )
    mocks.ecs.Secret.from_secrets_manager.assert_any_call(
        mocks.rds.DatabaseInstance.return_value.secret, field="password"
    )
