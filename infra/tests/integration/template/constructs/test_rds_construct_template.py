# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.constructs.rds import RdsConstruct, RdsConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config, vpc: ec2.Vpc) -> RdsConstruct:
    return RdsConstruct(stack, RdsConstructArgs(config, vpc))


@pytest.fixture(scope="module")
def task_role(roles: Mapping[str, Any], config: Config) -> Any | None:
    return next(
        (
            role
            for role in roles.values()
            if role["Properties"].get("RoleName")
            == f"{config.project_name}-{config.environment_name}-sql-task-role"
        ),
        None,
    )


def test_security_group(
    security_groups: Mapping[str, Any], vpcs: Mapping[str, Any]
) -> None:
    security_group = next(iter(security_groups.values()))
    vpc_id = next(iter(vpcs.keys()))

    assert security_group["Properties"]["GroupDescription"].endswith(
        "rds-security-group"
    )
    assert security_group["Properties"]["VpcId"] == {"Ref": vpc_id}

    ingress_rule = next(iter(security_group["Properties"]["SecurityGroupIngress"]))
    assert ingress_rule["Description"] == "Allow ECS to access RDS"
    assert ingress_rule["ToPort"] == 5432
    assert ingress_rule["FromPort"] == 5432
    assert ingress_rule["IpProtocol"] == "tcp"

    assert ingress_rule["CidrIp"] == {"Fn::GetAtt": [vpc_id, "CidrBlock"]}


def test_db_instance(config: Config, db_instances: Mapping[str, Any]) -> None:
    db_instance = next(iter(db_instances.values()))

    assert db_instance["Properties"]["DBName"] == config.project_name
    assert db_instance["Properties"]["Engine"] == "postgres"
    assert db_instance["Properties"]["EngineVersion"] == "16.4"
    assert db_instance["Properties"]["DBInstanceClass"] == "db.t3.micro"
    assert db_instance["Properties"]["AllocatedStorage"] == "100"
    assert db_instance["Properties"]["BackupRetentionPeriod"] == 7
    assert db_instance["Properties"]["PubliclyAccessible"] is False
    assert (
        db_instance["Properties"]["DBInstanceIdentifier"]
        == f"{config.project_name.lower()}-{config.environment_name}-rds-instance"
    )
