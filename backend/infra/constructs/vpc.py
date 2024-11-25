from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VpcConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.vpc = ec2.Vpc(self, "throwback-request-live-vpc", max_azs=2)
