from aws_cdk import CfnOutput
from config import Config
from constructs import IConstruct
from constructs.userpool import UserPoolConstruct
from stacks.stack import Stack

from infra.constructs.superuser import SuperUserConstruct


class UserManagementStack(Stack):

    def __init__(
        self,
        scope: IConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = "user-management",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.user_pool_construct = UserPoolConstruct(self, config)
        self.superuser_construct = SuperUserConstruct(
            self, config, self.user_pool_construct
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=self.superuser_construct.user_creation_task_definition.task_definition_arn,
        )
