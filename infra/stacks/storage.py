"""
This module defines the StorageStack class, which sets up the storage resources for the application.

It creates RDS and Cache constructs using the provided VPC and configuration.
"""

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from config import Config
from constructs import Construct
from constructs.cache import CacheConstruct
from constructs.rds import RdsConstruct
from stacks.stack import Stack


class StorageStack(Stack):
    """
    This stack sets up the storage resources for the application.

    It creates RDS and Cache constructs using the provided VPC and configuration.
    """

    def __init__(
        self,
        scope: Construct,
        config: Config,
        vpc: ec2.Vpc,
        stack_id: str | None = None,
    ) -> None:
        """
        Initialize the StorageStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            config (Config): The configuration object containing stack settings.
            vpc (ec2.Vpc): The VPC in which to create the storage resources.
            stack_id (str, optional): The ID of the stack.
                Defaults to f"{config.project_name}-{config.environment_name}-storage".
        """
        super().__init__(scope, config, stack_id, "storage")

        self.rds_construct = RdsConstruct(self, vpc, config)
        self.cache_construct = CacheConstruct(self, vpc, config)

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
