from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from constructs import Construct


class EnvironmentSetupStack(Stack):
    def __init__(
        self, scope: Construct, id: str, project_name, cluster: ecs.Cluster, **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.environment_setup_execution_role = iam.Role(
            self,
            "environment-setup-execution-role",
            role_name=f"{project_name}-environment-setup-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        self.security_group = ec2.SecurityGroup(
            self,
            "TaskSecurityGroup",
            vpc=cluster.vpc,
            description="Allow ECS tasks to communicate with RDS",
            allow_all_outbound=True,
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL access"
        )

        # Outputs for CICD pipeline
        CfnOutput(
            self, "security-group-id", value=self.security_group.security_group_id
        )

        # Dependency specific outputs
        CfnOutput(self, "ecs-cluster-name", value=cluster.cluster_name)
        CfnOutput(
            self,
            "subnet-id",
            value=cluster.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids[0],
        )
