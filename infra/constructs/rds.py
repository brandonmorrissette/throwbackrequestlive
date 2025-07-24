"""
This module contains the RdsConstruct class, which sets up an RDS instance
within a specified VPC. The construct includes security group configuration,
database instance creation, and ECS task definition for database schema deployment.

Classes:
    RdsConstruct: A construct that sets up an RDS instance.

Usage example:
    rds_construct = RdsConstruct(scope, vpc, config)
"""

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class RdsConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the RdsConstruct class.

    Attributes:
        config: Configuration object.
        uid: The ID of the construct.
            Defaults to "rds".
        prefix: The prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-rds".
        vpc: The VPC in which to create the RDS instance.
    """

    def __init__(
        self, config: Config, vpc: ec2.Vpc, uid: str = "rds", prefix: str = ""
    ) -> None:
        super().__init__(config=config, uid=uid, prefix=prefix)
        self.vpc = vpc


class RdsConstruct(Construct):
    """
    A construct that sets up an RDS instance.

    Attributes:
        db_instance: The RDS database instance.
        task_definition: The ECS task definition for database schema deployment.
        security_group: The security group for ECS tasks.

    Methods:
        __init__: Initializes the RdsConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: RdsConstructArgs,
    ) -> None:
        """
        Initializes the RdsConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (RdsConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        self.security_group = ec2.SecurityGroup(
            self, "rds-security-group", vpc=args.vpc
        )

        self.security_group.add_ingress_rule(
            ec2.Peer.ipv4(args.vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow ECS to access RDS",
        )

        self.db_instance = rds.DatabaseInstance(
            self,
            "rds-instance",
            database_name=args.config.project_name,
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=args.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            credentials=rds.Credentials.from_generated_secret(
                "db_master_user",
                secret_name=f"{args.config.project_name}-{args.config.environment_name}-db-credentials",  # pylint: disable=line-too-long
            ),
            allocated_storage=20,
            multi_az=False,
            publicly_accessible=False,
            backup_retention=Duration.days(7),
            security_groups=[self.security_group],
            instance_identifier=f"{args.config.project_name}-rds-instance",
        )

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
                    resources=[self.db_instance.secret.secret_arn],
                ),
                iam.PolicyStatement(
                    actions=["rds-db:connect"],
                    resources=[self.db_instance.instance_arn],
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
                "infra", file="setup/deploy_sql/Dockerfile"
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
                    self.db_instance.secret, field="username"
                ),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    self.db_instance.secret, field="password"
                ),
            },
            environment={
                "DB_HOST": self.db_instance.db_instance_endpoint_address,
            },
        )
