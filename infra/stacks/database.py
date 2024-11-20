from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from constructs.rds import RdsConstruct
from .stack import Stack

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, tags: dict, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, tags, **kwargs)
        self.rdsConstruct = RdsConstruct(self, "Rds", vpc=vpc)
