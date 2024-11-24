from aws_cdk import aws_ec2 as ec2, aws_iam as iam
from constructs import Construct


class DeploymentEc2Construct(Construct):
    def __init__(self, scope: Construct, id: str, vpc) -> None:
        super().__init__(scope, id)

        ec2_role = iam.Role(
            self,
            "EC2InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSFullAccess"),
            ],
        )

        ec2_security_group = ec2.SecurityGroup(self, "EC2SecurityGroup", vpc=vpc)
        ec2_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(22), "Allow SSH within VPC"
        )
        ec2_security_group.add_egress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.all_traffic(), "Allow outbound traffic"
        )

        self.deployment_ec2_instance = ec2.Instance(
            self,
            "DeploymentInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            role=ec2_role,
            security_group=ec2_security_group,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )
