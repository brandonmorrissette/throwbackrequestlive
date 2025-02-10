from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from config import Config
from constructs.construct import Construct


class RdsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        vpc,
        config: Config,
        id: str | None = None,
        suffix: str | None = "rds",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        rds_security_group = ec2.SecurityGroup(self, "rds-security-group", vpc=vpc)

        rds_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow ECS to access RDS",
        )

        self.db_instance = rds.DatabaseInstance(
            self,
            "rds-instance",
            database_name=config.project_name,
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            credentials=rds.Credentials.from_generated_secret(
                "db_master_user", secret_name=f"{config.project_name}-db-credentials"
            ),
            allocated_storage=20,
            multi_az=False,
            publicly_accessible=False,
            backup_retention=Duration.days(7),
            security_groups=[rds_security_group],
            instance_identifier=f"{config.project_name}-rds-instance",
        )

        task_role = iam.Role(
            self,
            "SQLTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "SQLTaskPolicy": iam.PolicyDocument(
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
                            resources=[
                                "*"
                            ],  # Adjust this to specific RDS resources if required
                        ),
                    ]
                )
            },
        )

        self.task_definition = ecs.FargateTaskDefinition(
            self,
            "sql-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=iam.Role(
                self,
                "sql-task-execution-role",
                role_name=f"{config.project_name}-sql-task-execution-role",
                assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AmazonECSTaskExecutionRolePolicy"
                    )
                ],
            ),
            task_role=task_role,
        )

        self.task_definition.add_container(
            "sql-container",
            image=ecs.ContainerImage.from_asset(
                "infra", file="setup/deploy_sql/Dockerfile"
            ),
            command=[
                "sh",
                "-c",
                'for file in /schema/*.sql; do echo "Running $file"; psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive -f $file; done',
            ],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="sql-deployment",
                log_group=logs.LogGroup(
                    self,
                    "sql-container-log-group",
                    log_group_name=f"/{config.project_name}-sql-container-logs-{self.node.id}",
                    removal_policy=RemovalPolicy.DESTROY,
                ),
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

        self.security_group = ec2.SecurityGroup(
            self,
            "TaskSecurityGroup",
            vpc=vpc,
            description="Allow ECS tasks to communicate with RDS",
            allow_all_outbound=True,
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL access"
        )

        admin_policy = iam.ManagedPolicy(
            self,
            "admin-rds-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "rds-db:connect",
                        "rds-db:executeStatement",
                        "rds-db:batchExecuteStatement",
                    ],
                    resources=[self.db_instance.instance_arn],
                )
            ],
        )

        admin_role = iam.Role(
            self,
            "admin-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
        )

        admin_role.add_managed_policy(admin_policy)
