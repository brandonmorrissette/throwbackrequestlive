from aws_cdk import aws_certificatemanager as acm, aws_route53 as route53
from constructs import Construct


class CertConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "hosed-zone",
            domain_name="throwbackrequestlive.com"
        )

        self.certificate = acm.Certificate(
            self, "site-certificate",
            domain_name="throwbackrequestlive.com",
            subject_alternative_names=["www.throwbackrequestlive.com"],
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )
