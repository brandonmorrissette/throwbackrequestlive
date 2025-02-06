from aws_cdk import CfnOutput
from config import Config
from constructs import Construct
from constructs.cluster import ClusterConstruct
from stacks.stack import Stack


class ComputeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc: str,
        id: str | None = None,
        suffix: str | None = "compute",
    ) -> None:
        super().__init__(scope, config, id=id, suffix=suffix)

        self.cluster_construct = ClusterConstruct(self, config, vpc=vpc)

        CfnOutput(
            self, "ecs-cluster-name", value=self.cluster_construct.cluster.cluster_name
        )
