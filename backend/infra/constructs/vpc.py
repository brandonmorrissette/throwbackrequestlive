from aws_cdk import aws_ec2 as ec2, CfnOutput
from constructs import Construct


class VpcConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.vpc = ec2.Vpc(self, "throwback-request-live-vpc", max_azs=2)
        CfnOutput(self, "subnet-id", value=self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT).subnet_ids[0], export_name="subnet-id")
