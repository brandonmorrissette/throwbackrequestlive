# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import assertions

from infra.config import Config
from infra.constructs.s3 import S3Construct
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def buckets(template: assertions.Template) -> Mapping[str, Any]:
    return template.find_resources("AWS::S3::Bucket")


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config) -> S3Construct:
    return S3Construct(stack, config)


def test_bucket_properties(buckets: Mapping[str, Any], config: Config) -> None:
    bucket = next(iter(buckets.values()))

    assert bucket["Properties"]["BucketName"] == (
        f"{config.project_name.lower() if config.project_name else None}-"
        f"{config.environment_name.lower() if config.environment_name else None}-bucket"
    )
    assert bucket["Properties"]["Tags"] == [
        {
            "Key": "aws-cdk:auto-delete-objects",
            "Value": "true",
        }
    ]


def test_ssm_parameter(
    ssm_parameters: Mapping[str, Any], buckets: Mapping[str, Any], config: Config
) -> None:
    parameter = next(iter(ssm_parameters.values()))

    assert parameter["Properties"]["Name"] == (
        f"/{config.project_name}-{config.environment_name}/bucket-name"
    )
    assert parameter["Properties"]["Value"] == {"Ref": next(iter(buckets.keys()))}
