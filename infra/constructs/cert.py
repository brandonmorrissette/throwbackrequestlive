"""
This module contains the CertConstruct class, which sets up an ACM certificate
within a specified hosted zone. The construct includes hosted zone lookup and certificate creation.

Classes:
    CertConstruct: A construct that sets up an ACM certificate.

Usage example:
    cert_construct = CertConstruct(scope, config)
"""

from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class CertConstruct(Construct):
    """
    A construct that sets up an ACM certificate.

    Attributes:
        hosted_zone: The Route 53 hosted zone.
        certificate: The ACM certificate.

    Methods:
        __init__: Initializes the CertConstruct with the given parameters.
    """

    def __init__(
        self, scope: Stack, config: Config, construct_id: str | None = None
    ) -> None:
        """
        Initializes the CertConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-cert".
        """
        super().__init__(scope, config, construct_id, "cert")

        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "hosed-zone", domain_name="throwbackrequestlive.com"
        )

        self.certificate = acm.Certificate(
            self,
            "site-certificate",
            domain_name="throwbackrequestlive.com",
            subject_alternative_names=["www.throwbackrequestlive.com"],
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
        )
