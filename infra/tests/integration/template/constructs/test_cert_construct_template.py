# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest

from infra.config import Config
from infra.constructs.cert import CertConstruct, CertConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config) -> CertConstruct:
    return CertConstruct(stack, CertConstructArgs(config))


def test_certificate(certificates: Mapping[str, Any]):
    assert len(certificates) == 1
    certificate = next(iter(certificates.values()))

    assert certificate["Properties"]["DomainName"] == "throwbackrequestlive.com"
    assert certificate["Properties"]["SubjectAlternativeNames"] == [
        "www.throwbackrequestlive.com"
    ]
    assert certificate["Properties"]["ValidationMethod"] == "DNS"
