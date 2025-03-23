# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import assertions
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager

from infra.config import Config
from infra.constructs.runtime import RuntimeConstruct, RuntimeConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def certificate(stack: Stack) -> acm.Certificate:
    return acm.Certificate(stack, "MockCertificate", domain_name="example.com")


@pytest.fixture(scope="module")
def policy_statement() -> iam.PolicyStatement:
    return iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["s3:GetObject"],
        resources=["arn:aws:s3:::mybucket/*"],
    )


@pytest.fixture(scope="module")
def policy(stack: Stack, policy_statement: iam.PolicyStatement) -> iam.ManagedPolicy:
    return iam.ManagedPolicy(
        stack,
        "MockPolicy",
        statements=[policy_statement],
        managed_policy_name="MockPolicy",
    )


@pytest.fixture(scope="module")
def cluster(stack: Stack) -> ecs.Cluster:
    return ecs.Cluster(stack, "MockCluster")


@pytest.fixture(scope="module")
def runtime_variables() -> dict:
    return {"ENV_VAR_KEY": "env-var-value"}


@pytest.fixture(scope="module")
def runtime_secrets(stack: Stack) -> dict:
    runtime_secret = secretsmanager.Secret(
        stack,
        "MockRuntimeSecret",
        generate_secret_string=secretsmanager.SecretStringGenerator(
            password_length=32, exclude_punctuation=True
        ),
    )
    return {"RuntimeSecret": ecs.Secret.from_secrets_manager(runtime_secret)}


@pytest.fixture(scope="module")
def runtime_construct_args(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    config: Config,
    certificate: acm.Certificate,
    policy: iam.ManagedPolicy,
    cluster: ecs.Cluster,
    runtime_variables: dict,
    runtime_secrets: dict,
) -> RuntimeConstructArgs:
    return RuntimeConstructArgs(
        config=config,
        certificate=certificate,
        policy=policy,
        cluster=cluster,
        runtime_variables=runtime_variables,
        runtime_secrets=runtime_secrets,
    )


@pytest.fixture(scope="module", autouse=True)
def construct(
    stack: Stack,
    runtime_construct_args: RuntimeConstructArgs,
) -> RuntimeConstruct:
    return RuntimeConstruct(
        stack,
        args=runtime_construct_args,
    )


@pytest.fixture(scope="module")
def secrets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::SecretsManager::Secret")


@pytest.fixture(scope="module")
def services(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ECS::Service")


@pytest.fixture(scope="module")
def target_groups(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ElasticLoadBalancingV2::TargetGroup")


def test_jwt_secret(secrets: Mapping[str, Any]) -> None:
    jwt_secret = next(
        (secret for key, secret in secrets.items() if "JWTSecret" in key), None
    )

    assert jwt_secret
    assert jwt_secret["Properties"]["GenerateSecretString"] == {
        "ExcludePunctuation": True,
        "PasswordLength": 32,
    }


def test_policy(
    managed_policies: Mapping[str, Any], secrets: Mapping[str, Any], config: Config
) -> None:
    policy = next(
        policy
        for policy in managed_policies.values()
        if f"{config.project_name}-{config.environment_name}-runtime-policy"
        == policy["Properties"]["ManagedPolicyName"]
    )

    assert policy
    assert {
        "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
        "Effect": "Allow",
        "Resource": {"Ref": next(key for key in secrets if "JWTSecret" in key)},
    } in policy["Properties"]["PolicyDocument"]["Statement"]


def test_task_role(
    roles: Mapping[str, Any], config: Config, managed_policies: Mapping[str, Any]
) -> None:
    task_role = next(
        (
            role
            for role in roles.values()
            if f"{config.project_name}-{config.environment_name}-runtime-task-role"
            == role["Properties"]["RoleName"]
        ),
        None,
    )

    assert task_role
    assert task_role["Properties"]["AssumeRolePolicyDocument"]["Statement"] == [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
        }
    ]

    expected_policies = [
        {
            "Fn::Join": [
                "",
                [
                    "arn:",
                    {"Ref": "AWS::Partition"},
                    ":iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
                ],
            ]
        },
        {
            "Ref": next(
                (
                    id
                    for id, policy in managed_policies.items()
                    if f"{config.project_name}-{config.environment_name}-runtime-policy"
                    == policy["Properties"]["ManagedPolicyName"]
                ),
                None,
            )
        },
        {
            "Ref": next(
                (
                    id
                    for id, policy in managed_policies.items()
                    if policy["Properties"]["ManagedPolicyName"] == "MockPolicy"
                ),
                None,
            )
        },
    ]

    assert all(
        policy in task_role["Properties"]["ManagedPolicyArns"]
        for policy in expected_policies
    )


def test_task_definition(
    task_definitions: Mapping[str, Any],
    runtime_variables: Mapping[str, Any],
    roles: Mapping[str, Any],
    secrets: Mapping[str, Any],
    config: Config,
) -> None:
    task_definition = next(iter(task_definitions.values()))

    assert task_definition["Properties"]["Cpu"] == "256"
    assert task_definition["Properties"]["RequiresCompatibilities"] == ["FARGATE"]
    assert task_definition["Properties"]["TaskRoleArn"]["Fn::GetAtt"] == [
        next(
            (
                id
                for id, role in roles.items()
                if f"{config.project_name}-{config.environment_name}-runtime-task-role"
                == role["Properties"]["RoleName"]
            ),
            None,
        ),
        "Arn",
    ]

    container_definition = next(
        iter(task_definition["Properties"]["ContainerDefinitions"])
    )
    assert container_definition["PortMappings"] == [
        {"ContainerPort": 5000, "Protocol": "tcp"}
    ]
    assert container_definition["Environment"] == [
        {"Name": key, "Value": value} for key, value in runtime_variables.items()
    ]

    expected_secrets = [
        {
            "Name": "JWT_SECRET_KEY",
            "ValueFrom": {
                "Ref": next(
                    (
                        key
                        for key in secrets.keys()
                        if f"{config.project_name}{config.environment_name}runtimeJWTSecret"
                        in key
                    ),
                    None,
                )
            },
        },
        {
            "Name": "RuntimeSecret",
            "ValueFrom": {
                "Ref": next(
                    (key for key in secrets.keys() if "MockRuntimeSecret" in key),
                    None,
                )
            },
        },
    ]
    assert all(secret in container_definition["Secrets"] for secret in expected_secrets)


def test_service(
    services: Mapping[str, Any],
    clusters: Mapping[str, Any],
    task_definitions: Mapping[str, Any],
) -> None:
    service = next(iter(services.values()))

    assert service["Properties"]["Cluster"] == {"Ref": next(iter(clusters.keys()))}
    assert service["Properties"]["LaunchType"] == "FARGATE"
    assert service["Properties"]["DesiredCount"] == 1
    assert service["Properties"]["TaskDefinition"] == {
        "Ref": next(iter(task_definitions.keys()))
    }


def test_logging(log_groups: Mapping[str, Any], config: Config) -> None:
    log_group = next(iter(log_groups.values()))

    assert log_group["Properties"]["RetentionInDays"] == 7
    assert (
        log_group["Properties"]["LogGroupName"]
        == f"/{config.project_name}-{config.environment_name}-runtime"
    )
    assert log_group["UpdateReplacePolicy"] == "Delete"
    assert log_group["DeletionPolicy"] == "Delete"


def test_health_check(
    target_groups: Mapping[str, Any],
) -> None:
    target_group = next(iter(target_groups.values()))

    assert target_group["Properties"]["HealthCheckIntervalSeconds"] == 30
    assert target_group["Properties"]["HealthCheckPath"] == "/"
    assert target_group["Properties"]["HealthCheckTimeoutSeconds"] == 10
