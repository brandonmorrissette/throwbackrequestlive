from aws_cdk import aws_ec2 as ec2
from aws_cdk import Stack
from constructs import Construct
from constructs.rds import RdsConstruct

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.rdsConstruct = RdsConstruct(self, "Rds", vpc=vpc)
