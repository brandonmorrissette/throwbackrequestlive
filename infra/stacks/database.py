from aws_cdk import Stack
from constructs import Construct
from constructs.rds import RdsConstruct


class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc_id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.database = RdsConstruct(self, "Rds", vpc=vpc_id)
