from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs.cluster import ClusterConstruct
from constructs.construct import Construct
from stacks.stack import Stack


class ComputeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc: ec2.Vpc,
        id: str | None = None,
        suffix: str | None = "compute",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.cluster_construct = ClusterConstruct(self, config, vpc=vpc)

        CfnOutput(
            self, "ecs-cluster-name", value=self.cluster_construct.cluster.cluster_name
        )
