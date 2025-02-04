import boto3
from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from config import Config
from constructs import Construct
from constructs.userpool import UserPoolConstruct
from stacks.stack import Stack


class SuperUserConstruct(Construct):
    def __init__(
        self, scope: Construct, config: Config, user_pool_construct: UserPoolConstruct
    ) -> None:
        super().__init__(scope, "superuser-construct")
        superuser_group = cognito.CfnUserPoolGroup(
            self,
            "SuperuserGroup",
            user_pool_id=user_pool_construct.user_pool.user_pool_id,
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
                            f"arn:aws:cognito-idp:{config.cdk_environment.region}:{config.cdk_environment.account}:userpool/{user_pool_construct.user_pool.user_pool_id}"
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
                                f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool_construct.user_pool.user_pool_id}"
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

        self.task_definition = ecs.FargateTaskDefinition(
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
            task_role=superuser_task_role,
        )

        self.task_definition.add_container(
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
