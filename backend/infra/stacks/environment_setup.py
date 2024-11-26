from aws_cdk import Stack, aws_ecs as ecs, aws_ec2 as ec2, aws_iam as iam, aws_s3 as s3, CfnOutput, aws_secretsmanager as secretsmanager, aws_ssm as ssm, RemovalPolicy
from constructs import Construct

class EnvironmentSetupStack(Stack):
    def __init__(self, scope: Construct, id: str, cluster: ecs.Cluster, rds_secret: secretsmanager.ISecret, project_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        schema_bucket = s3.Bucket(
            self, "SchemaBucket",
            bucket_name=f"{project_name.lower()}-schema-files",
            removal_policy=RemovalPolicy.DESTROY, 
            auto_delete_objects=True
        )
        
        environment_setup_execution_role = iam.Role(
            self, "environment-setup-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        sql_task_role = iam.Role(
            self, "SQLTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "SQLTaskPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret"
                            ],
                            resources=[rds_secret.secret_arn]
                        ),
                        iam.PolicyStatement(
                            actions=["rds-db:connect"],
                            resources=["*"]  # Adjust this to specific RDS resources if required
                        ),
                        iam.PolicyStatement(
                            actions=["s3:GetObject"],
                            resources=[f"{schema_bucket.bucket_arn}/*"]
                        )
                    ]
                )
            }
        )

        sql_task_definition = ecs.FargateTaskDefinition(
            self, "sql-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=environment_setup_execution_role,
            task_role=sql_task_role
        )

        sql_task_definition.add_container(
            "sql-container",
            image=ecs.ContainerImage.from_asset(
                "backend/infra", 
                file="environment_setup/deploy_sql/Dockerfile"  
            ),
            secrets={
                "DB_HOST": ecs.Secret.from_secrets_manager(rds_secret, "host"),
                "DB_USER": ecs.Secret.from_secrets_manager(rds_secret, "username"),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(rds_secret, "password")
            },
            command=[
                "sh",
                "-c",
                "for file in /schema/*.sql; do echo \"Running $file\"; psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive -f $file; done"
            ],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="sql-deployment")
        )

        security_group = ec2.SecurityGroup(
            self, "TaskSecurityGroup",
            vpc=cluster.vpc,
            description="Allow ECS tasks to communicate with RDS",
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL access"
        )

        superuser_task_role = iam.Role(
            self, "SuperuserTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "SuperuserPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["ssm:GetParameter"],
                            resources=[
                                f"arn:aws:ssm:{self.region}:{self.account}:parameter/{project_name}/{project_name}-user-pool-id"
                            ]
                        )
                    ]
                )
            }
        )

        superuser_task_definition = ecs.FargateTaskDefinition(
            self, "superuser-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=environment_setup_execution_role,
            task_role=superuser_task_role
        )

        superuser_task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset(
                "backend/infra/environment_setup/create_superuser"
            ),
            environment={
                "USER_POOL_ID": ssm.StringParameter.from_string_parameter_name(
                    self,
                    f"{project_name}-user-pool-id",
                    string_parameter_name=f"/{project_name}/{project_name}-user-pool-id"
                ).string_value,
                "SUPERUSER_EMAIL": "admin@example.com"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="superuser-creation")
        )



        # Outputs for CICD pipeline
        CfnOutput(self, "schema-bucket-name", value=schema_bucket.bucket_name)
        CfnOutput(self, "security-group-id", value=security_group.security_group_id)
        CfnOutput(self, "sql-task-definition-arn", value=sql_task_definition.task_definition_arn)
        CfnOutput(self, "superuser-task-definition-arn", value=superuser_task_definition.task_definition_arn)

        # Dependency specific outputs
        CfnOutput(self, "ecs-cluster-name", value=cluster.cluster_name)
        CfnOutput(self, "subnet-id", value=cluster.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT).subnet_ids[0])
