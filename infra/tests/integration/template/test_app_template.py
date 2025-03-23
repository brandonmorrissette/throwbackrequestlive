# pylint: disable=missing-module-docstring, missing-function-docstring, redefined-outer-name
import importlib
import os

import aws_cdk as cdk
import pytest

PROJECT_NAME = "AppTemplateTest"
ENVIRONMENT_NAME = "IntegrationTesting"


@pytest.fixture(scope="module")
def invocation():
    os.environ["PROJECT_NAME"] = PROJECT_NAME
    os.environ["ENVIRONMENT_NAME"] = ENVIRONMENT_NAME
    os.environ["AWS_ACCOUNT"] = "IntegrationTestAccount"
    os.environ["AWS_REGION"] = "us-east-1"
    from infra import app  # pylint: disable=import-outside-toplevel

    importlib.reload(app)

    return app


@pytest.fixture(scope="module")
def stacks(invocation):
    stacks = [
        child for child in invocation.app.node.children if isinstance(child, cdk.Stack)
    ]

    del os.environ["PROJECT_NAME"]
    del os.environ["ENVIRONMENT_NAME"]
    del os.environ["AWS_ACCOUNT"]
    del os.environ["AWS_REGION"]

    return stacks


def test_expected_stacks_exist(stacks):
    expected_stack_ids = {
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-user-management",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-network",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-compute",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-storage",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-runtime",
    }

    stack_ids = {stack.node.id for stack in stacks}

    assert expected_stack_ids.issubset(
        stack_ids
    ), f"Missing stacks: {expected_stack_ids - stack_ids}"


def test_compute_stack_dependencies(stacks):
    compute_stack = _get_stack_by_name(
        stacks, f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-compute"
    )

    dependency_ids = {dep.node.id for dep in compute_stack.dependencies}
    expected_dependencies = {
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-network",
    }

    assert expected_dependencies.issubset(dependency_ids), (
        "ComputeStack dependencies incorrect. Expected:"
        f"{expected_dependencies}, Found: {dependency_ids}"
    )


def test_storage_stack_dependencies(stacks):
    storage_stack = _get_stack_by_name(
        stacks, f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-storage"
    )

    dependency_ids = {dep.node.id for dep in storage_stack.dependencies}
    expected_dependencies = {
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-network",
    }

    assert expected_dependencies.issubset(dependency_ids), (
        f"StorageStack dependencies incorrect. Expected:"
        f"{expected_dependencies}, Found: {dependency_ids}"
    )


def test_runtime_stack_dependencies(stacks):
    runtime_stack = _get_stack_by_name(
        stacks, f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-runtime"
    )

    dependency_ids = {dep.node.id for dep in runtime_stack.dependencies}
    expected_dependencies = {
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-user-management",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-network",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-compute",
        f"{PROJECT_NAME}-{ENVIRONMENT_NAME}-storage",
    }

    assert expected_dependencies.issubset(dependency_ids), (
        f"RuntimeStack dependencies incorrect. Expected:"
        f"{expected_dependencies}, Found: {dependency_ids}"
    )


def _get_stack_by_name(stacks, stack_name):
    return next((stack for stack in stacks if stack.node.id == stack_name), None)
