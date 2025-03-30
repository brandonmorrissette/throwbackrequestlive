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
    assert db_instance["Properties"]["AllocatedStorage"] == "20"
    assert db_instance["Properties"]["BackupRetentionPeriod"] == 7
    assert db_instance["Properties"]["PubliclyAccessible"] is False
    assert (
        db_instance["Properties"]["DBInstanceIdentifier"]
        == f"{config.project_name.lower()}-rds-instance"
    )


def test_policy(
    managed_policies: Mapping[str, Any],
    secret_target_attachment: Mapping[str, Any],
    db_instances: Mapping[str, Any],
    config: Config,
) -> None:
    policy = next(
        (
            policy
            for policy in managed_policies.values()
            if policy["Properties"].get("ManagedPolicyName")
            == f"{config.project_name}-{config.environment_name}-sql-task-policy"
        ),
        None,
    )

    assert policy
    expected_statements = [
        {
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
            ],
            "Effect": "Allow",
            "Resource": {"Ref": next(iter(secret_target_attachment.keys()))},
        },
        {
            "Action": "rds-db:connect",
            "Effect": "Allow",
            "Resource": {
                "Fn::Join": [
                    "",
                    [
                        "arn:",
                        {"Ref": "AWS::Partition"},
                        f":rds:{config.cdk_environment.region}:"
                        f"{config.cdk_environment.account}:db:",
                        {"Ref": next(iter(db_instances.keys()))},
                    ],
                ]
            },
        },
    ]
    assert all(
        statement in policy["Properties"]["PolicyDocument"]["Statement"]
        for statement in expected_statements
    )


# pylint: disable=R0801
def test_task_role(
    task_role: Mapping[str, Any], managed_policies: Mapping[str, Any]
) -> None:
    assert task_role
    assert task_role["Properties"]["AssumeRolePolicyDocument"]["Statement"] == [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
        }
    ]
    assert task_role["Properties"]["ManagedPolicyArns"] == [
        {"Ref": next(iter(managed_policies.keys()))}
    ]


def test_task_definition(
    task_definitions: Mapping[str, Any],
    roles: Mapping[str, Any],
    task_role: Mapping[str, Any],
) -> None:
    task_definition = next(iter(task_definitions.values()))

    assert task_definition["Properties"]["RequiresCompatibilities"] == ["FARGATE"]

    assert task_definition["Properties"]["TaskRoleArn"]["Fn::GetAtt"] == [
        next(key for key, value in roles.items() if value == task_role),
        "Arn",
    ]


def test_container_definition(
    task_definitions: Mapping[str, Any],
    db_instances: Mapping[str, Any],
    log_groups: Mapping[str, Any],
    secret_target_attachment: Mapping[str, Any],
) -> None:
    task_definition = next(iter(task_definitions.values()))

    container_definition = next(
        iter(task_definition["Properties"]["ContainerDefinitions"])
    )

    assert container_definition["Name"] == "sql-container"
    assert container_definition["Command"] == [
        "sh",
        "-c",
        'for file in /schema/*.sql; do echo "Running $file"; '
        "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/"
        "throwbackrequestlive -f $file; done",
    ]

    logging_options = container_definition["LogConfiguration"]["Options"]
    assert logging_options["awslogs-group"] == {"Ref": next(iter(log_groups.keys()))}
    assert logging_options["awslogs-stream-prefix"] == "sql-deployment"

    assert {
        "Name": "DB_USER",
        "ValueFrom": {
            "Fn::Join": [
                "",
                [{"Ref": next(iter(secret_target_attachment.keys()))}, ":username::"],
            ]
        },
    } in container_definition["Secrets"]

    assert {
        "Name": "DB_PASSWORD",
        "ValueFrom": {
            "Fn::Join": [
                "",
                [{"Ref": next(iter(secret_target_attachment.keys()))}, ":password::"],
            ]
        },
    } in container_definition["Secrets"]

    assert container_definition["Environment"] == [
        {
            "Name": "DB_HOST",
            "Value": {
                "Fn::GetAtt": [
                    next(iter(db_instances.keys())),
                    "Endpoint.Address",
                ]
            },
        }
    ]
