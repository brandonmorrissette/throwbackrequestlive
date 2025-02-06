from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from config import Config
from constructs import Construct
from resources.resource import Resource


class VpcConstruct(Construct, Resource):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:

        Resource.__init__(self, scope, config, id, suffix)
        super().__init__(self.scope, self.id)

        self.vpc = ec2.Vpc(self, self.id, max_azs=2)
