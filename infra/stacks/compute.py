from aws_cdk import CfnOutput, Stack
from constructs import Construct
from constructs.cluster import ClusterConstruct


class ComputeStack(Stack):
    def __init__(
        self, scope: Construct, id: str, project_name, env, vpc: str, **kwargs
    ):
        super().__init__(scope, id, env=env, **kwargs)
        self.cluster_construct = ClusterConstruct(
            self, "cluster", project_name=project_name, vpc=vpc
        )
        CfnOutput(
            self, "ecs-cluster-name", value=self.cluster_construct.cluster.cluster_name
        )
