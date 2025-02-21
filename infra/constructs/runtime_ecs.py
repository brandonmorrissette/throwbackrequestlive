from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from config import Config
from constructs.construct import Construct


class RuntimeEcsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        certificate,
        vpc,
        db_instance,
        id: str | None = None,
        suffix: str | None = "runtime-ecs",
    ) -> None:
        super().__init__(scope, config, id, suffix)

        jwt_secret = secretsmanager.Secret(
            self,
            "JWTSecret",
            description="JWT secret for secure token generation",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=32, exclude_punctuation=True
            ),
        )

        user_pool_id = ssm.StringParameter.from_string_parameter_name(
            self, "UserPoolId", f"{config.project_name}-user-pool-id"
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
                                "cognito-idp:ListUsers",
                            ],
                            resources=[
                                f"arn:aws:cognito-idp:{config.cdk_environment.region}:{config.cdk_environment.account}:userpool/{user_pool_id}"
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
                string_parameter_name=f"/{config.project_name}/ecs-cluster-name",
            ).string_value,
            vpc=vpc,
        )

        docker_image = ecr_assets.DockerImageAsset(
            self, f"{config.project_name}-{config.project_name}-image", directory="."
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
                    stream_prefix=config.project_name,
                    log_group=aws_logs.LogGroup(
                        self,
                        "log-group",
                        retention=aws_logs.RetentionDays.ONE_WEEK,
                        removal_policy=RemovalPolicy.DESTROY,
                    ),
                ),
                environment={
                    "COGNITO_APP_CLIENT_ID": ssm.StringParameter.from_string_parameter_name(
                        self,
                        "AppClientId",
                        f"{config.project_name}-user-pool-app-client-id",
                    ).string_value,
                    "COGNITO_USER_POOL_ID": user_pool_id,
                    "DB_NAME": config.project_name,
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
                    "JWT_SECRET_KEY": ecs.Secret.from_secrets_manager(jwt_secret),
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
