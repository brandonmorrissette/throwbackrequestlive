# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import aws_cdk as cdk
import pytest
from aws_cdk import aws_ec2 as ec2

from infra.config import Config
from infra.stacks.show import ShowStack, ShowStackArgs


@pytest.fixture(scope="module")
def app() -> cdk.App:
    return cdk.App()


@pytest.fixture(scope="module")
def config() -> Config:
    return Config(
        "ShowSynthTest",
        "IntegrationTesting",
        cdk.Environment(account="IntegrationTestAccount", region="us-east-1"),
    )


@pytest.fixture(scope="module")
def stack(app: cdk.App, config: Config, vpc: ec2.Vpc) -> ShowStack:
    return ShowStack(app, ShowStackArgs(config, vpc))


def test_cache_cluster(cache_clusters: Mapping[str, Any]) -> None:
    assert len(cache_clusters) == 1
