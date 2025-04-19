# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest

from infra.config import Config
from infra.constructs.vpc import VpcConstruct, VpcConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config) -> VpcConstruct:
    return VpcConstruct(stack, VpcConstructArgs(config))


def test_vpc_creation(vpcs: Mapping[str, Any]) -> None:
    vpc = next(iter(vpcs.values()))

    assert vpc
