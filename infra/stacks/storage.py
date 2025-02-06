from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs import Construct
from constructs.rds import RdsConstruct
from stacks.stack import Stack


class StorageStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc: ec2.Vpc,
        id: str | None = None,
        suffix: str | None = "storage",
    ):
        super().__init__(scope, config, id=id, suffix=suffix)

        self.rds_construct = RdsConstruct(self, vpc, config)

        CfnOutput(
            self,
            "security-group-id",
            value=self.rds_construct.security_group.security_group_id,
        )

        CfnOutput(
            self,
            "sql-task-definition-arn",
            value=self.rds_construct.task_definition.task_definition_arn,
        )
