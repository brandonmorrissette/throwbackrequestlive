from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class ClusterConstruct(Construct):
    def __init__(
        self,
        scope: Stack,
        config: Config,
        vpc: ec2.Vpc,
        id: str | None = None,
        suffix: str | None = "cluster",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.cluster = ecs.Cluster(self, self.id, vpc=vpc)
