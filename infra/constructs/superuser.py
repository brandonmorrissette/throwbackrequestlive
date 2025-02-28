from aws_cdk import RemovalPolicy
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk.aws_cognito import CfnUserPoolGroup
from config import Config
from constructs.construct import Construct
from constructs.userpool import UserPoolConstruct


class SuperUserConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        user_pool_id: str | None,
        id: str | None = None,
        suffix: str | None = "superuser",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        self.policy = iam.ManagedPolicy(
            self,
            "cognito-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "cognito-idp:AdminGetUser",
                        "cognito-idp:AdminCreateUser",
                        "cognito-idp:AdminDeleteUser",
                        "cognito-idp:AdminUpdateUserAttributes",
                        "cognito-idp:AdminAddUserToGroup",
                        "cognito-idp:AdminRemoveUserFromGroup",
                        "cognito-idp:AdminCreateGroup",
                        "cognito-idp:AdminDeleteGroup",
                        "cognito-idp:AdminUpdateGroup",
                        "cognito-idp:AdminAddUserToGroup",
                        "cognito-idp:ListUsers",
                        "cognito-idp:AdminListGroupsForUser",
                    ],
                    resources=[
                        f"arn:aws:cognito-idp:{config.cdk_environment.region}:{config.cdk_environment.account}:userpool/{user_pool_id}"
                    ],
                )
            ],
        )

        role = iam.Role(
            self,
            "superuser-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
        )

        role.add_managed_policy(self.policy)

        CfnUserPoolGroup(
            self,
            "superuser-group",
            group_name="superuser",
            user_pool_id=user_pool_id,
            description="Superuser group with elevated permissions",
            role_arn=role.role_arn,
        )

        user_creation_task_role = iam.Role(
            self,
            "SuperuserTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[self.policy],
            inline_policies={
                "SuperuserPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cognito-idp:ListUserPools",
                            ],
                            resources=["*"],
                        ),
                    ]
                )
            },
        )

        user_creation_task_definition = ecs.FargateTaskDefinition(
            self,
            "superuser-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=iam.Role(
                self,
                "superuser-execution-role",
                role_name=f"{config.project_name}-superuser-execution-role",
                assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AmazonECSTaskExecutionRolePolicy"
                    )
                ],
            ),
            task_role=user_creation_task_role,
        )

        user_creation_task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset("infra/setup/create_superuser"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="superuser-creation",
                log_group=logs.LogGroup(
                    self,
                    "superuser-container-log-group",
                    log_group_name=f"/ecs/{config.project_name}-superuser-container-logs-{self.node.id}",
                    removal_policy=RemovalPolicy.DESTROY,
                ),
            ),
        )

        self.superuser_task_definition_arn = (
            user_creation_task_definition.task_definition_arn
        )
