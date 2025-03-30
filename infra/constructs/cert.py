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

from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class CertConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the CertConstruct.

    Attributes:
        config (Config): Configuration object.
        uid (str): The ID of the construct.
            Default is "cert".
        prefix (str): The prefix for the construct ID.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config,
        uid: str = "cert",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


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
        self,
        scope: Stack,
        args: CertConstructArgs,
    ) -> None:
        """
        Initializes the CertConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (CertConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

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
