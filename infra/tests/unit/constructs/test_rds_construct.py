# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import ANY, MagicMock, patch

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
    duration: MagicMock
    _lambda: MagicMock


@pytest.fixture(scope="module")
def mock_rds_construct(vpc: ec2.Vpc, config: Config, stack: Stack):
    with patch("infra.constructs.rds.ec2") as mock_ec2, patch(
        "infra.constructs.rds.rds"
    ) as mock_rds, patch("infra.constructs.rds.Duration") as mock_duration, patch(
        "infra.constructs.rds._lambda"
    ) as mock_lambda:

        yield RdsConstruct(stack, RdsConstructArgs(config, vpc)), Mocks(
            mock_ec2, mock_rds, mock_duration, mock_lambda
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
        "rds-instance",
        database_name=config.project_name,
        engine=ANY,
        instance_type=ANY,
        vpc=vpc,
        vpc_subnets=mocks.ec2.SubnetSelection.return_value,
        credentials=ANY,
        multi_az=False,
        publicly_accessible=False,
        backup_retention=mocks.duration.days(7),
        security_groups=[mocks.ec2.SecurityGroup.return_value],
        instance_identifier=f"{config.project_name}-{config.environment_name}-rds-instance",
    )

    mocks.rds.DatabaseInstanceEngine.postgres.assert_called_once_with(
        version=mocks.rds.PostgresEngineVersion.VER_16_4
    )

    mocks.ec2.SubnetSelection.assert_called_once_with(
        subnet_type=mocks.ec2.SubnetType.PUBLIC
    )

    mocks.ec2.InstanceType.of.assert_called_once_with(
        mocks.ec2.InstanceClass.BURSTABLE3, mocks.ec2.InstanceSize.MICRO
    )

    mocks.rds.Credentials.from_generated_secret.assert_called_once_with(
        "db_master_user",
        secret_name=f"{config.project_name}-{config.environment_name}-db-credentials",
    )
