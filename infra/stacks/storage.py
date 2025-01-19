from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from constructs import Construct
from constructs.rds import RdsConstruct


class StorageStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.Vpc,
        project_name: str,
        log_group,
        security_group,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.rds_construct = RdsConstruct(
            self, "rds", vpc=vpc, project_name=project_name
        )

        sql_task_role = iam.Role(
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
                            resources=[
                                self.rds_construct.db_instance.secret.secret_arn
                            ],
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

        sql_task_definition = ecs.FargateTaskDefinition(
            self,
            "sql-task-definition",
            memory_limit_mib=512,
            cpu=256,
            # I'd rather use the environment setup execution role, but it keeps causing a circular dependency
            # due to the container requiring secrets. It's been a real tail chase.
            execution_role=iam.Role(
                self,
                "sql-task-execution-role",
                role_name=f"{project_name}-sql-task-execution-role",
                assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AmazonECSTaskExecutionRolePolicy"
                    )
                ],
            ),
            task_role=sql_task_role,
        )

        sql_task_definition.add_container(
            "sql-container",
            image=ecs.ContainerImage.from_asset(
                "infra", file="environment_setup/deploy_sql/Dockerfile"
            ),
            command=[
                "sh",
                "-c",
                'for file in /schema/*.sql; do echo "Running $file"; psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive -f $file; done',
            ],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="sql-deployment",
                log_group=log_group,
            ),
            secrets={
                "DB_USER": ecs.Secret.from_secrets_manager(
                    self.rds_construct.db_instance.secret, field="username"
                ),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    self.rds_construct.db_instance.secret, field="password"
                ),
            },
            environment={
                "DB_HOST": self.rds_construct.db_instance.db_instance_endpoint_address,
            },
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL access"
        )

        CfnOutput(
            self,
            "sql-task-definition-arn",
            value=sql_task_definition.task_definition_arn,
        )
