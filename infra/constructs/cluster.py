from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ssm as ssm
from config import Config
from constructs import Construct


class ClusterConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc,
        id: str | None = None,
        suffix: str | None = "-cluster",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.cluster = ecs.Cluster(self, self.id, vpc=vpc)

        ssm.StringParameter(
            self,
            "EcsClusterNameParam",
            parameter_name=f"/{config.project_name}/ecs-cluster-name",
            string_value=self.cluster.cluster_name,
        )
