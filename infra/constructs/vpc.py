from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs.construct import Construct
from resources.resource import Resource


class VpcConstruct(Construct, Resource):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        id: str | None = None,
        suffix: str | None = "vpc",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.vpc = ec2.Vpc(self, self.id, max_azs=2)
