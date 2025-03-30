# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import pytest
from constructs import Construct

from infra.aspects.tagging import TaggingAspect
from infra.config import Config
from infra.tests import conftest


@pytest.fixture
def mock_construct() -> MagicMock:
    return MagicMock(spec=Construct)


@pytest.fixture
def aspect(config: Config) -> TaggingAspect:
    return TaggingAspect(config)


def test_tagging_aspect_initialization(aspect, config):
    assert aspect.config == config


def test_given_project_name_when_visit_then_tag_added(aspect, mock_construct):
    with patch("infra.aspects.tagging.Tags") as mock_tags:
        aspect.visit(mock_construct)

    mock_tags.of.assert_any_call(mock_construct)
    mock_tags.of.return_value.add.assert_any_call("project_name", conftest.PROJECT_NAME)


def test_given_environment_name_when_visit_then_tag_added(aspect, mock_construct):
    with patch("infra.aspects.tagging.Tags") as mock_tags:
        aspect.visit(mock_construct)

    mock_tags.of.assert_any_call(mock_construct)
    mock_tags.of.return_value.add.assert_any_call(
        "environment_name", conftest.ENVIRONMENT_NAME
    )


def test_tagging_aspect_skips_nodes_without_node_attribute(aspect):
    mock_construct_without_node = MagicMock()
    del mock_construct_without_node.node

    with patch("infra.aspects.tagging.Tags") as mock_tags:
        aspect.visit(mock_construct_without_node)

    mock_tags.of(mock_construct_without_node).add.assert_not_called()
