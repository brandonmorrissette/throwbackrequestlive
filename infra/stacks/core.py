from aws_cdk import Stack, CfnOutput
from constructs import Construct
from constructs.vpc import VpcConstruct
from constructs.cert import CertConstruct


class CoreStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = VpcConstruct(self, "Vpc")
        cert = CertConstruct(self, "Cert")

        self.vpc_output = CfnOutput(self, "VpcId", value=self.vpc.vpc.vpc_id)
        self.certificate_output = CfnOutput(
            self, "CertificateArn", value=cert.certificate.certificate_arn
        )
