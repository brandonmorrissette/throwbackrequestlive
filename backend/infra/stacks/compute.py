from aws_cdk import Stack
from constructs import Construct
from constructs.cluster import ClusterConstruct
from aws_cdk import Stack

class ComputeStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.cluster_construct = ClusterConstruct(self, "cluster", vpc=vpc)
