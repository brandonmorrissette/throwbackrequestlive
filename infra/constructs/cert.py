from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from config import Config
from constructs import Construct
from resources.resource import Resource


class CertConstruct(Construct, Resource):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        Resource.__init__(self, scope, config, id, suffix)
        super().__init__(self.scope, self.id)

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
