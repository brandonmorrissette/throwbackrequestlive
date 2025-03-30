# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from infra.resources.resource import Resource, ResourceArgs
from infra.tests import conftest


def test_format_id_with_default_prefix(config):
    resource = Resource()
    result = resource.format_id(ResourceArgs(config))
    assert result == f"{conftest.PROJECT_NAME}-{conftest.ENVIRONMENT_NAME}"


def test_format_id_with_custom_prefix(config):
    resource = Resource()
    result = resource.format_id(ResourceArgs(config, prefix="CustomPrefix"))
    assert result == "CustomPrefix"


def test_format_id_with_uid(config):
    resource = Resource()
    result = resource.format_id(ResourceArgs(config, uid="ResourceId"))
    assert result == f"{conftest.PROJECT_NAME}-{conftest.ENVIRONMENT_NAME}-ResourceId"


def test_format_id_with_custom_prefix_and_resource_id(config):
    resource = Resource()
    result = resource.format_id(
        ResourceArgs(config, uid="ResourceId", prefix="CustomPrefix")
    )
    assert result == "CustomPrefix-ResourceId"
