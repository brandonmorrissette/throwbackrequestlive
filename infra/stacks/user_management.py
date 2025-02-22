from aws_cdk import CfnOutput
from config import Config
from constructs import IConstruct
from constructs.superuser import SuperUserConstruct
from constructs.userpool import UserPoolConstruct
from stacks.stack import Stack


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
            self, config, self.user_pool_construct.user_pool.user_pool_id
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=self.superuser_construct.superuser_task_definition_arn,
        )
