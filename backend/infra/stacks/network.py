from constructs import Construct
from constructs.vpc import VpcConstruct
from constructs.cert import CertConstruct
from aws_cdk import Stack

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.vpcConstruct = VpcConstruct(self, "Vpc")
        self.certConstruct = CertConstruct(self, "Cert")