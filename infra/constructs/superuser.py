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

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack

# pylint: disable=R0801
PERMITTED_ACTIONS = [
    "cognito-idp:AdminGetUser",
    "cognito-idp:AdminCreateUser",
    "cognito-idp:AdminDeleteUser",
    "cognito-idp:AdminUpdateUserAttributes",
    "cognito-idp:AdminAddUserToGroup",
    "cognito-idp:AdminRemoveUserFromGroup",
    "cognito-idp:AdminCreateGroup",
    "cognito-idp:AdminDeleteGroup",
    "cognito-idp:AdminUpdateGroup",
    "cognito-idp:ListUserPools",
    "cognito-idp:AdminListGroupsForUser",
    "cognito-idp:ListUsers",
]


class SuperUserConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the SuperUserConstruct class.

    Attributes:
        config: Configuration object.
        user_pool_id (str): The ID of the Cognito user pool.
        uid (str, optional): The ID of the construct.
            Defaults to "superuser".
        prefix (str, optional): The prefix for the construct ID.
            Defaults to f"{config.project_name}-{config.environment_name}-superuser".
    """

    def __init__(
        self,
        config: Config,
        user_pool_id: str,
        uid: str = "superuser",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.user_pool_id = user_pool_id


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
        args: SuperUserConstructArgs,
    ) -> None:
        """
        Initializes the SuperUserConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (SuperUserConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        user_pool_resource_arn = (
            f"arn:aws:cognito-idp:{args.config.cdk_environment.region}:"
            f"{args.config.cdk_environment.account}:userpool/{args.user_pool_id}"
        )

        self.policy = iam.ManagedPolicy(
            self,
            "cognito-policy",
            managed_policy_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-cognito-policy",
            statements=[
                iam.PolicyStatement(
                    actions=PERMITTED_ACTIONS,
                    resources=[
                        user_pool_resource_arn,
                    ],
                )
            ],
        )

        role = iam.Role(
            self,
            "superuser-role",
            role_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-superuser-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            managed_policies=[self.policy],
        )

        CfnUserPoolGroup(
            self,
            "superuser-group",
            group_name="superuser",
            user_pool_id=args.user_pool_id,
            description="Superuser group with elevated permissions",
            role_arn=role.role_arn,
        )

        task_role = iam.Role(
            self,
            "SuperuserTaskRole",
            role_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-superuser-task-role",
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
            task_role=task_role,
        )

        log_group = logs.LogGroup(
            self,
            "superuser-container-log-group",
            log_group_name=f"{args.config.project_name}-{args.config.environment_name}-superuser-container-logs",  # pylint: disable=line-too-long
            removal_policy=RemovalPolicy.DESTROY,
        )

        user_creation_task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset("infra/setup/create_superuser"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="superuser-creation", log_group=log_group
            ),
        )

        self.user_creation_task_def_arn = (
            user_creation_task_definition.task_definition_arn
        )
