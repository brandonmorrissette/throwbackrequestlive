from aws_cdk import Stack
from constructs import Construct
from constructs.cluster import ClusterConstruct


class ClusterStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc_id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.cluster = ClusterConstruct(self, "Cluster", vpc=vpc_id).cluster
