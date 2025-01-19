from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class RuntimeEcsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name,
        certificate,
        env,
        vpc,
        db_instance,
        **kwargs,
    ) -> None:
        super().__init__(scope, id)

        docker_image = ecr_assets.DockerImageAsset(
            self, "throwback-request-live-image", directory="."
        )

        jwt_secret = secretsmanager.Secret(
            self,
            "JWTSecret",
            description="JWT secret for secure token generation",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=32, exclude_punctuation=True
            ),
        )

        user_pool_id = ssm.StringParameter.from_string_parameter_name(
            self, "UserPoolId", f"{project_name}-user-pool-id"
        ).string_value

        task_role = iam.Role(
            self,
            "CustomTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
            ],
            inline_policies={
                "CustomPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cognito-idp:AdminListGroupsForUser",
                                "cognito-idp:AdminGetUser",
                            ],
                            resources=[
                                f"arn:aws:cognito-idp:{env.region}:{env.account}:userpool/{user_pool_id}"
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[jwt_secret.secret_arn],
                        ),
                    ]
                )
            },
        )

        cluster = ecs.Cluster.from_cluster_attributes(
            self,
            "ImportedCluster",
            cluster_name=ssm.StringParameter.from_string_parameter_name(
                self,
                "EcsClusterNameParam",
                string_parameter_name=f"/{project_name}/ecs-cluster-name",
            ).string_value,
            vpc=vpc,
        )

        self.runtime_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "runtime-service",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(docker_image),
                container_port=5000,
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="throwback-request-live",
                    log_group=aws_logs.LogGroup(
                        self, "log-group", retention=aws_logs.RetentionDays.ONE_WEEK
                    ),
                ),
                environment={
                    "COGNITO_APP_CLIENT_ID": ssm.StringParameter.from_string_parameter_name(
                        self, "AppClientId", f"{project_name}-user-pool-app-client-id"
                    ).string_value,
                    "COGNITO_USER_POOL_ID": user_pool_id,
                    "JWT_SECRET": jwt_secret.secret_value.to_string(),
                    "DB_NAME": ssm.StringParameter.from_string_parameter_name(
                        self, "DbName", f"/{project_name}/db-name"
                    ).string_value,
                    "DB_ENGINE": db_instance.engine.engine_type,
                },
                secrets={
                    "DB_USER": ecs.Secret.from_secrets_manager(
                        db_instance.secret, field="username"
                    ),
                    "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                        db_instance.secret, field="password"
                    ),
                    "DB_HOST": ecs.Secret.from_secrets_manager(
                        db_instance.secret, field="host"
                    ),
                },
                task_role=task_role,
            ),
            public_load_balancer=True,
            certificate=certificate,
            redirect_http=True,
            health_check_grace_period=Duration.minutes(5),
        )

        self.runtime_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200",
        )
