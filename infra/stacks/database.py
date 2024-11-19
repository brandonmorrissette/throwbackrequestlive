from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct
from constructs.rds import RdsConstruct


class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.rdsConstruct = RdsConstruct(self, "Rds", vpc=vpc)
