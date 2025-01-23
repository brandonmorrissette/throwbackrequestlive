from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class VpcConstruct(Construct):
    def __init__(self, scope: Construct, id: str, project_name) -> None:
        super().__init__(scope, id)

        self.vpc = ec2.Vpc(self, f"{project_name}-vpc", max_azs=2)
        ssm.StringParameter(
            self,
            "VpcIdParam",
            parameter_name=f"/{project_name}/vpc-id",
            string_value=self.vpc.vpc_id,
        )
        CfnOutput(
            self,
            "subnet-id",
            value=self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids[0],
        )
