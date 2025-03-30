# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import aws_cdk as cdk
import pytest
from aws_cdk import Stack as AwsCdkStack

from infra.config import Config
from infra.resources.resource import Resource
from infra.stacks.stack import Stack, StackArgs

UID = "TestStack"
PREFIX = "TestPrefix"
RESOURCE_ID = "TestResource"


@pytest.fixture(scope="module")
def scope(app: cdk.App):
    return AwsCdkStack(app, "TestScope")


@pytest.fixture(scope="module")
def args(config: Config):
    return StackArgs(config, UID, PREFIX)


@pytest.fixture(scope="module")
def mock_stack(scope: AwsCdkStack, args: StackArgs):
    with patch.object(Resource, "format_id") as mock_format_id:
        mock_format_id.return_value = RESOURCE_ID
        construct = Stack(scope, args)

        yield construct, mock_format_id


def test_stack_inheritance():
    assert issubclass(Stack, AwsCdkStack)
    assert issubclass(Stack, Resource)


def test_stack_initialization(mock_stack: tuple[Stack, MagicMock], args: StackArgs):
    stack, mock_format_id = mock_stack

    mock_format_id.assert_called_once_with(args)

    assert stack.node.id == RESOURCE_ID
