from aws_cdk import Stack
from constructs import Construct
from constructs.cluster import ClusterConstruct


class ComputeStack(Stack):
    def __init__(self, scope: Construct, id: str, project_name, vpc: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.cluster_construct = ClusterConstruct(self, "cluster", project_name=project_name, vpc=vpc)
