from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs import Construct
from constructs.cert import CertConstruct
from constructs.vpc import VpcConstruct
from stack import Stack


class NetworkStack(Stack):
    def __init__(self, scope: Construct, config: Config) -> None:
        super().__init__(scope, config, suffix="network")

        self.vpc_constrcut = VpcConstruct(self, "vpc", project_name=config.project_name)
        self.cert_construct = CertConstruct(self, "cert")

        CfnOutput(
            self,
            "subnet-id",
            value=self.vpc_constrcut.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids[0],
        )
