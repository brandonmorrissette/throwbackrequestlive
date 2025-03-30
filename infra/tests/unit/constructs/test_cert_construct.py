# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import MagicMock, patch

import pytest
from constructs import Construct

from infra.config import Config
from infra.constructs.cert import CertConstruct, CertConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module")
def mock_cert_construct(config: Config, stack: Stack):
    with patch("infra.constructs.cert.route53") as mock_route53, patch(
        "infra.constructs.cert.acm"
    ) as mock_acm:
        construct = CertConstruct(stack, CertConstructArgs(config))

        yield construct, mock_route53, mock_acm


def test_construct_inheritance():
    assert issubclass(CertConstruct, Construct)


def test_default_id(
    mock_cert_construct: tuple[CertConstruct, MagicMock, MagicMock], config: Config
):
    cert_construct, _, _ = mock_cert_construct
    assert (
        cert_construct.node.id
        == f"{config.project_name}-{config.environment_name}-cert"
    )


def test_hosted_zone_lookup(
    mock_cert_construct: tuple[CertConstruct, MagicMock, MagicMock],
):
    cert_construct, mock_route53, mock_acm = mock_cert_construct

    mock_route53.HostedZone.from_lookup.assert_called_once_with(
        cert_construct, "hosed-zone", domain_name="throwbackrequestlive.com"
    )


def test_certificate_creation(
    mock_cert_construct: tuple[CertConstruct, MagicMock, MagicMock],
):
    cert_construct, mock_route53, mock_acm = mock_cert_construct

    mock_acm.Certificate.assert_called_once_with(
        cert_construct,
        "site-certificate",
        domain_name="throwbackrequestlive.com",
        subject_alternative_names=["www.throwbackrequestlive.com"],
        validation=mock_acm.CertificateValidation.from_dns.return_value,
    )
