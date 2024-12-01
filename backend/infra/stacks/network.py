from aws_cdk import Stack
from constructs import Construct
from constructs.cert import CertConstruct
from constructs.vpc import VpcConstruct


class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, project_name, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.vpc_constrcut = VpcConstruct(self, "vpc", project_name=project_name)
        self.cert_construct = CertConstruct(self, "cert")
