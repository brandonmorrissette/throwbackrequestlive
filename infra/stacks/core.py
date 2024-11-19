from aws_cdk import Stack
from constructs import Construct
from constructs.vpc import VpcConstruct
from constructs.cert import CertConstruct


class CoreStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpcConstruct = VpcConstruct(self, "Vpc")
        self.certConstruct = CertConstruct(self, "Cert")
