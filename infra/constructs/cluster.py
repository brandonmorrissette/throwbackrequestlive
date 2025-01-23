from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ssm as ssm
from aws_cdk import CfnOutput
from constructs import Construct


class ClusterConstruct(Construct):
    def __init__(self, scope: Construct, id: str, project_name, vpc) -> None:
        super().__init__(scope, id)

        self.cluster = ecs.Cluster(self, "throwback-request-live-cluster", vpc=vpc)
        ssm.StringParameter(
            self,
            "EcsClusterNameParam",
            parameter_name=f"/{project_name}/ecs-cluster-name",
            string_value=self.cluster.cluster_name,
        )
        CfnOutput(self, "ecs-cluster-name", value=self.cluster.cluster_name)
