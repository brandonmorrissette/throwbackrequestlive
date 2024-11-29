from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from constructs import Construct
from constructs.rds import RdsConstruct


class StorageStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.Vpc,
        project_name: str,
        execution_role,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        self.rds_construct = RdsConstruct(
            self, "rds", vpc=vpc, project_name=project_name
        )

        schema_bucket = s3.Bucket(
            self,
            "SchemaBucket",
            bucket_name=f"{project_name.lower()}-schema-files",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
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
                        iam.PolicyStatement(
                            actions=["s3:GetObject"],
                            resources=[f"{schema_bucket.bucket_arn}/*"],
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
            execution_role=execution_role,
            task_role=sql_task_role,
        )

        sql_task_definition.add_container(
            "sql-container",
            image=ecs.ContainerImage.from_asset(
                "backend/infra", file="environment_setup/deploy_sql/Dockerfile"
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
                    "deploy-sql-task-log-group",
                    log_group_name=f"/ecs/{project_name}-deploy-sql-task-logs",
                ),
            ),
        )

        CfnOutput(self, "schema-bucket-name", value=schema_bucket.bucket_name)
        CfnOutput(
            self,
            "sql-task-definition-arn",
            value=sql_task_definition.task_definition_arn,
        )
