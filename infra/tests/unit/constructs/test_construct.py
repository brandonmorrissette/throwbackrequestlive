# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest
from constructs import Construct as AwsCdkConstruct

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.resources.resource import Resource

UID = "TestConstruct"
PREFIX = "TestPrefix"
RESOURCE_ID = "TestResource"


@pytest.fixture(scope="module")
def scope(app: cdk.App):
    return AwsCdkConstruct(app, "TestScope")


@pytest.fixture(scope="module")
def construct_args(config: Config):
    return ConstructArgs(config, UID, PREFIX)


@pytest.fixture(scope="module")
def mock_construct(scope: AwsCdkConstruct, construct_args: ConstructArgs):
    with patch.object(Resource, "format_id") as mock_format_id:
        mock_format_id.return_value = RESOURCE_ID
        construct = Construct(scope, construct_args)

        yield construct, mock_format_id


def test_construct_inheritance():
    assert issubclass(Construct, AwsCdkConstruct)
    assert issubclass(Construct, Resource)


def test_construct_initialization(
    mock_construct: tuple[Construct, MagicMock], construct_args: ConstructArgs
):
    construct, mock_format_id = mock_construct

    mock_format_id.assert_called_once_with(construct_args)

    assert construct.node.id == RESOURCE_ID
