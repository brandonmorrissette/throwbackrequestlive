# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import Stack as AwsCdkStack
from aws_cdk import assertions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam

from infra.config import Config
from infra.stacks.stack import Stack, StackArgs

PROJECT_NAME = "UnitTestProject"
ENVIRONMENT_NAME = "UnitTestEnv"
STACK_NAME = "TestStack"
ACCOUNT = "unittest"
REGION = "us-east-1"


@pytest.fixture(scope="module")
def app():
    return cdk.App()


@pytest.fixture(scope="module")
def config():
    return Config(
        project_name=PROJECT_NAME,
        environment_name=ENVIRONMENT_NAME,
        cdk_environment=cdk.Environment(account=ACCOUNT, region=REGION),
    )


@pytest.fixture(scope="module")
def stack_args(config: Config):
    return StackArgs(config)


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config):
    return AwsCdkStack(app, STACK_NAME, env=config.cdk_environment)


@pytest.fixture(scope="module")
def subnet():
    return ec2.SubnetConfiguration(
        name="PrivateSubnet",
        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
        cidr_mask=24,
    )


@pytest.fixture(scope="module")
def vpc(stack: Stack, subnet: ec2.SubnetConfiguration):
    return ec2.Vpc(
        stack,
        "Vpc",
        subnet_configuration=[
            subnet,
            ec2.SubnetConfiguration(
                name="PublicSubnet",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24,
            ),
        ],
    )


@pytest.fixture(scope="module")
def secrets_policy():
    return iam.PolicyStatement(
        actions=[
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
        ]
    )


@pytest.fixture(scope="module")
def ecs_task_role():
    return {
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    }
                ]
            }
        }
    }


@pytest.fixture(scope="module")
def template(stack: Stack):
    return assertions.Template.from_stack(stack)


@pytest.fixture(scope="module")
def security_groups(template: assertions.Template):
    return template.find_resources("AWS::EC2::SecurityGroup")


@pytest.fixture(scope="module")
def vpcs(template: assertions.Template):
    return template.find_resources("AWS::EC2::VPC")


@pytest.fixture(scope="module")
def subnet_groups(template: assertions.Template):
    return template.find_resources("AWS::ElastiCache::SubnetGroup")


@pytest.fixture(scope="module")
def roles(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::IAM::Role")


@pytest.fixture(scope="module")
def db_instances(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::RDS::DBInstance")


@pytest.fixture(scope="module")
def log_groups(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Logs::LogGroup")


@pytest.fixture(scope="module")
def task_definitions(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ECS::TaskDefinition")


@pytest.fixture(scope="module")
def secret_target_attachment(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::SecretsManager::SecretTargetAttachment")


@pytest.fixture(scope="module")
def managed_policies(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::IAM::ManagedPolicy")


@pytest.fixture(scope="module")
def load_balancers(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ElasticLoadBalancingV2::LoadBalancer")


@pytest.fixture(scope="module")
def clusters(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ECS::Cluster")


@pytest.fixture(scope="module")
def certificates(template: assertions.Template):
    return template.find_resources("AWS::CertificateManager::Certificate")


@pytest.fixture(scope="module")
def cache_clusters(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ElastiCache::CacheCluster")


@pytest.fixture(scope="module")
def user_pool_groups(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Cognito::UserPoolGroup")


@pytest.fixture(scope="module")
def user_groups(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Cognito::UserPoolGroup")


@pytest.fixture(scope="module")
def user_pools(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Cognito::UserPool")


@pytest.fixture(scope="module")
def user_pool_clients(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Cognito::UserPoolClient")


@pytest.fixture(scope="module")
def ssm_parameters(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::SSM::Parameter")


@pytest.fixture(scope="module")
def record_sets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Route53::RecordSet")


@pytest.fixture(scope="module")
def record_target(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Route53::RecordSetTarget")


@pytest.fixture(scope="module")
def hosted_zones(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::Route53::HostedZone")


@pytest.fixture(scope="module")
def secrets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::SecretsManager::Secret")


@pytest.fixture(scope="module")
def services(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ECS::Service")


@pytest.fixture(scope="module")
def target_groups(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::ElasticLoadBalancingV2::TargetGroup")


@pytest.fixture
def subnets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::EC2::Subnet")


@pytest.fixture
def policies(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::IAM::Policy")
