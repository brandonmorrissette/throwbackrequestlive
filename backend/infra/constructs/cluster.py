from aws_cdk import aws_ecs as ecs, CfnOutput

from constructs import Construct


class ClusterConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc) -> None:
        super().__init__(scope, id)

        self.cluster = ecs.Cluster(self, "ThrowbackRequestLiveCluster", vpc=vpc)
        CfnOutput(self, "ECSClusterName", value=self.cluster.cluster_name)
