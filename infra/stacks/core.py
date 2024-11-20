from constructs import Construct
from constructs.vpc import VpcConstruct
from constructs.cert import CertConstruct
from .stack import Stack

class CoreStack(Stack):
    def __init__(self, scope: Construct, id: str, tags: dict, **kwargs):
        super().__init__(scope, id, tags, **kwargs)
        self.vpcConstruct = VpcConstruct(self, "Vpc")
        self.certConstruct = CertConstruct(self, "Cert")