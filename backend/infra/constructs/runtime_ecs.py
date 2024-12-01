from aws_cdk import Duration
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class RuntimeEcsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, project_name, cluster, certificate) -> None:
        super().__init__(scope, id)

        docker_image = ecr_assets.DockerImageAsset(
            self, "throwback-request-live-image",
            directory="."
        )

        jwt_secret = secretsmanager.Secret(
            self, 
            "JWTSecret", 
            description="JWT secret for secure token generation", 
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=32,
                exclude_punctuation=True
            )
        )

        self.runtime_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "runtime-service",
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
                        self, "log-group",
                        retention=aws_logs.RetentionDays.ONE_WEEK
                    )
                ),
                environment = {
                    "COGNITO_APP_CLIENT_ID": ssm.StringParameter.from_string_parameter_name(
                        self, "AppClientId", f"{project_name}-user-pool-app-client-id"
                    ).string_value,
                    "COGNITO_USER_POOL_ID": ssm.StringParameter.from_string_parameter_name(
                        self, "UserPoolId", f"{project_name}-user-pool-id"
                    ).string_value,
                    "JWT_SECRET": jwt_secret.secret_value.to_string()
                }
            ),
            public_load_balancer=True,
            certificate=certificate,
            redirect_http=True,
            health_check_grace_period=Duration.minutes(5)
        )

        self.runtime_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200"
        )
