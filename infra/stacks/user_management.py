import boto3
from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from config import Config
from constructs import Construct
from constructs.userpool import UserPoolConstruct


class UserManagementStack(Stack):

    def __init__(
        self,
        scope: Construct,
        config: Config,
    ) -> None:
        super().__init__(
            scope,
            f"{config.project_name}-{config.environment_name}-user-management",
            env=config.cdk_environment,
        )

        self._cognito_client = boto3.client("cognito-idp")
        project_name = config.project_name
        user_pool_name = f"{project_name}-user-pool"
        self.user_pool_construct = UserPoolConstruct(
            self,
            f"{project_name}-user-pool-construct",
            user_pool_name,
            self._cognito_client,
        )

        admin_group = cognito.CfnUserPoolGroup(
            self,
            "admin-group",
            user_pool_id=self.user_pool_construct.user_pool.user_pool_id,
            group_name="admin",
        )

        superuser_group = cognito.CfnUserPoolGroup(
            self,
            "SuperuserGroup",
            user_pool_id=self.user_pool_construct.user_pool.user_pool_id,
            group_name="superuser",
        )

        superuser_role = iam.Role(
            self,
            "superuser-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
        )
        superuser_role.add_managed_policy(
            iam.ManagedPolicy(
                self,
                "cognito-policy",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "cognito-idp:AdminCreateUser",
                            "cognito-idp:AdminDeleteUser",
                            "cognito-idp:AdminUpdateUserAttributes",
                            "cognito-idp:AdminAddUserToGroup",
                            "cognito-idp:AdminRemoveUserFromGroup",
                            "cognito-idp:AdminCreateGroup",
                            "cognito-idp:AdminDeleteGroup",
                            "cognito-idp:AdminUpdateGroup",
                        ],
                        resources=[
                            f"arn:aws:cognito-idp:{config.cdk_environment.region}:{config.cdk_environment.account}:userpool/{self.user_pool_construct.user_pool.user_pool_id}"
                        ],
                    )
                ],
            )
        )

        superuser_task_role = iam.Role(
            self,
            "SuperuserTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "SuperuserPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cognito-idp:AdminGetUser",
                                "cognito-idp:AdminCreateUser",
                                "cognito-idp:AdminAddUserToGroup",
                            ],
                            resources=[
                                f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{self.user_pool_construct.user_pool.user_pool_id}"
                            ],
                        ),
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

        superuser_task_definition = ecs.FargateTaskDefinition(
            self,
            "superuser-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=iam.Role(
                self,
                "superuser-execution-role",
                role_name=f"{project_name}-superuser-execution-role",
                assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AmazonECSTaskExecutionRolePolicy"
                    )
                ],
            ),
            task_role=superuser_task_role,
        )

        superuser_task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset("infra/setup/create_superuser"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="superuser-creation",
                log_group=logs.LogGroup(
                    self,
                    "superuser-container-log-group",
                    log_group_name=f"/ecs/{project_name}-superuser-container-logs-{self.node.id}",
                    removal_policy=RemovalPolicy.DESTROY,
                ),
            ),
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=superuser_task_definition.task_definition_arn,
        )
