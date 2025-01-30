from aws_cdk import CfnOutput, Stack
from config import Config
from constructs import Construct
from constructs.cluster import ClusterConstruct


class ComputeStack(Stack):
    def __init__(self, scope: Construct, config: Config, vpc: str):
        super().__init__(
            scope,
            f"{config.project_name}-{config.environment_name}-compute",
            env=config.cdk_environment,
        )
        self.cluster_construct = ClusterConstruct(
            self, "cluster", project_name=config.project_name, vpc=vpc
        )
        CfnOutput(
            self, "ecs-cluster-name", value=self.cluster_construct.cluster.cluster_name
        )
