from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from constructs.cert import CertConstruct
from constructs.vpc import VpcConstruct


class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, project_name, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.vpc_constrcut = VpcConstruct(self, "vpc", project_name=project_name)
        self.cert_construct = CertConstruct(self, "cert")

        CfnOutput(
            self,
            "subnet-id",
            value=self.vpc_constrcut.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids[0],
        )
