"""
This module contains the SuperUserConstruct class,
which sets up the superuser task for the ECS cluster.

Classes:
    SuperUserConstruct: A construct that sets up the superuser task.

Usage example:
    superuser_task_construct = SuperUserConstruct(scope, config, user_pool_id)
"""

from aws_cdk import RemovalPolicy
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class SuperUserConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the SuperUserConstruct.

    Attributes:
        config (Config): Configuration object.
        user_pool_id (str): The ID of the Cognito user pool.
        uid (str): The ID of the construct.
            Default is "cluster".
        prefix (str): The prefix for the construct ID.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        user_pool_id: str,
        uid: str = "superuser-task",
        prefix: str = "",
    ):
        super().__init__(config, uid, prefix)
        self.user_pool_id = user_pool_id


class SuperUserConstruct(Construct):
    """
    A construct that sets up the superuser task.

    Attributes:
        db_instance: The RDS database instance.

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

        policy = iam.ManagedPolicy(
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

        task_role = iam.Role(
            self,
            "SuperuserTaskRole",
            role_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-superuser-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[policy],
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

        self.task_definition = ecs.FargateTaskDefinition(
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

        self.task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset("infra/deployment/superuser/create"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="superuser-creation", log_group=log_group
            ),
        )
