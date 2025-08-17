"""
This module contains the SqlDeploymentConstruct class, which sets up the SQL deployment for the rds.

Classes:
    SqlDeploymentConstruct: A construct that sets up the SQL deployment.

Usage example:
    sql_task_construct = SqlTaskConstruct(scope, config)
"""

from aws_cdk import RemovalPolicy
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class SqlDeploymentConstructArgs(
    ConstructArgs
):  # pylint: disable=too-few-public-methods
    """
    Arguments for the SqlDeploymentConstruct.

    Attributes:
        config (Config): Configuration object.
        db_instance (rds.IDatabaseInstance): The RDS database instance.
        uid (str): The ID of the construct.
            Default is "cluster".
        prefix (str): The prefix for the construct ID.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        db_instance: rds.IDatabaseInstance,
        uid: str = "sql-deployment",
        prefix: str = "",
    ):
        super().__init__(config, uid, prefix)
        self.db_instance = db_instance


class SqlDeploymentConstruct(Construct):
    """
    A construct that sets up the SQL deployment.

    Attributes:
        db_instance: The RDS database instance.

    Methods:
        __init__: Initializes the SqlTaskConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: SqlDeploymentConstructArgs,
    ) -> None:
        """
        Initializes the SqlTaskConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (SqlTaskConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        policy = iam.ManagedPolicy(
            self,
            "sql-task-policy",
            managed_policy_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-sql-task-policy",
            # pylint: disable=R0801
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                    ],
                    resources=[args.db_instance.secret.secret_arn],
                ),
                iam.PolicyStatement(
                    actions=["rds-db:connect"],
                    resources=[args.db_instance.instance_arn],
                ),
            ],
        )

        task_role = iam.Role(
            self,
            "sql-task-role",
            role_name=f"{args.config.project_name}-{args.config.environment_name}-sql-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[policy],
        )

        self.task_definition = ecs.FargateTaskDefinition(
            self,
            "sql-task-definition",
            # pylint: disable=duplicate-code
            memory_limit_mib=512,
            cpu=256,
            task_role=task_role,
        )

        log_group = logs.LogGroup(
            self,
            "sql-container-log-group",
            log_group_name=f"/{args.config.project_name}-{args.config.environment_name}-sql-container-logs",  # pylint: disable=line-too-long
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.task_definition.add_container(
            "sql-container",
            image=ecs.ContainerImage.from_asset(
                "infra", file="deployment/sql/Dockerfile"
            ),
            command=[
                "sh",
                "-c",
                'echo "Running entrypoints.sql"; '
                "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive "
                "-f /schema/entrypoints.sql; "
                'echo "Running shows.sql"; '
                "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive "
                "-f /schema/shows.sql; "
                'echo "Running songs.sql"; '
                "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive "
                "-f /schema/songs.sql; "
                'echo "Running requests.sql"; '
                "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive "
                "-f /schema/requests.sql; "
                'echo "Running submissions.sql"; '
                "psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive "
                "-f /schema/submissions.sql;",
            ],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="sql-deployment",
                log_group=log_group,
            ),
            secrets={
                "DB_USER": ecs.Secret.from_secrets_manager(
                    args.db_instance.secret, field="username"
                ),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    args.db_instance.secret, field="password"
                ),
            },
            environment={
                "DB_HOST": args.db_instance.db_instance_endpoint_address,
            },
        )
