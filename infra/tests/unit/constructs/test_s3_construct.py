# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from dataclasses import dataclass
from unittest.mock import ANY, MagicMock, patch

import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.s3 import S3Construct
from infra.stacks.stack import Stack


@dataclass
class Mocks:  # pylint: disable=missing-class-docstring
    s3: MagicMock
    ssm: MagicMock


@pytest.fixture(scope="module")
def mock_s3_construct(config: Config, stack: Stack):
    with patch("infra.constructs.s3.s3") as mock_s3, patch(
        "infra.constructs.s3.ssm"
    ) as mock_ssm:
        yield S3Construct(stack, config), Mocks(mock_s3, mock_ssm)


def test_construct_inheritance():
    assert issubclass(S3Construct, Construct)


def test_bucket_creation(mock_s3_construct: tuple[S3Construct, Mocks], config: Config):
    construct, mocks = mock_s3_construct

    mocks.s3.Bucket.assert_called_once_with(
        construct,
        ANY,
        bucket_name=(
            f"{config.project_name.lower() if config.project_name else None}-"
            f"{config.environment_name.lower() if config.environment_name else None}-bucket"
        ),
        removal_policy=ANY,
        auto_delete_objects=True,
    )


def test_ssm_parameter_creation(
    mock_s3_construct: tuple[S3Construct, Mocks], config: Config
):
    construct, mocks = mock_s3_construct

    mocks.ssm.StringParameter.assert_called_once_with(
        construct,
        ANY,
        parameter_name=f"/{config.project_name}-{config.environment_name}/bucket-name",
        string_value=mocks.s3.Bucket.return_value.bucket_name,
    )
