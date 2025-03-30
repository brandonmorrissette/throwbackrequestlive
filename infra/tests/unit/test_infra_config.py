# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
import aws_cdk as cdk
import pytest

from infra.config import Config

PROJECT_NAME = "TestProject"
ENVIRONMENT_NAME = "TestEnvironment"
CDK_ENVIRONMENT = cdk.Environment(account="123456789012", region="us-east-1")


@pytest.fixture(scope="module")
def config():
    return Config(PROJECT_NAME, ENVIRONMENT_NAME, CDK_ENVIRONMENT)


def test_config_initialization(config: Config):
    assert config.project_name == PROJECT_NAME
    assert config.environment_name == ENVIRONMENT_NAME
    assert config.cdk_environment == CDK_ENVIRONMENT


def test_config_str_representation(config: Config):
    assert (
        str(config)
        == f"Config(project_name={PROJECT_NAME}, environment_name={ENVIRONMENT_NAME}, cdk_environment={CDK_ENVIRONMENT})"  # pylint: disable=line-too-long
    )
