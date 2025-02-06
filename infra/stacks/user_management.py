from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from config import Config
from constructs import Construct
from constructs.user import SuperUserConstruct
from constructs.userpool import UserPoolConstruct
from stacks.stack import Stack


class UserManagementStack(Stack):

    def __init__(
        self,
        scope: Construct,
        config: Config,
        id: str | None = None,
        suffix: str | None = "user-management",
    ) -> None:
        super().__init__(scope, config, id=id, suffix=suffix)

        self.user_pool_construct = UserPoolConstruct(self, config)
        self.superuser_construct = SuperUserConstruct(
            self, config, self.user_pool_construct
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=self.superuser_construct.task_definition.task_definition_arn,
        )
