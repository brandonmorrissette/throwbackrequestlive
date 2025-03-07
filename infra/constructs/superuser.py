"""
This module contains the SuperUserConstruct class, which sets up a Cognito user pool group
in a given user pool with elevated permissions and an ECS task definition for user creation.

Classes:
    SuperUserConstruct: A construct that sets up a Cognito user pool group 
        and an ECS task definition for user creation.

Usage example:
    superuser_construct = SuperUserConstruct(scope, config, user_pool_id)
"""

from aws_cdk import RemovalPolicy
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk.aws_cognito import CfnUserPoolGroup
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class SuperUserConstruct(Construct):
    """
    A construct that sets up a Cognito user pool group in a given user pool
        and an ECS task definition for user creation.

    Attributes:
        policy: The IAM managed policy for the superuser role.
        superuser_task_definition_arn: The ARN of the ECS task definition for user creation.

    Methods:
        __init__: Initializes the SuperUserConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        config: Config,
        user_pool_id: str,
        construct_id: str | None = None,
    ) -> None:
        """
        Initializes the SuperUserConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            user_pool_id (str): The ID of the Cognito user pool.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-superuser".
            suffix (str, optional): Suffix for resource names. Defaults to "superuser".
        """
        super().__init__(scope, config, construct_id, "superuser")

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
                        f"arn:aws:cognito-idp:{config.cdk_environment.region}:"
                        f"{config.cdk_environment.account}:userpool/{user_pool_id}"
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
                    log_group_name=f"/ecs/{config.project_name}"
                    f"-superuser-container-logs-{self.node.id}",
                    removal_policy=RemovalPolicy.DESTROY,
                ),
            ),
        )

        self.user_creation_task_def_arn = (
            user_creation_task_definition.task_definition_arn
        )
