from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager
from config import Config
from constructs.construct import Construct
from stacks.stack import Stack


class RuntimeEcsConstruct(Construct):
    def __init__(
        self,
        scope: Stack,
        config: Config,
        certificate: acm.Certificate,
        policy: iam.ManagedPolicy,
        cluster: ecs.Cluster,
        runtime_variables: dict,
        runtime_secrets: dict,
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

        runtime_secrets.update(
            {
                "JWT_SECRET_KEY": ecs.Secret.from_secrets_manager(jwt_secret),
            }
        )

        task_role = iam.Role(
            self,
            "RuntimeTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                policy,
            ],
            inline_policies={
                "RuntimePolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[jwt_secret.secret_arn],
                        ),
                    ]
                )
            },
        )

        docker_image = ecr_assets.DockerImageAsset(
            self, f"{config.project_name}-{config.project_name}-image", directory="."
        )

        runtime_service = ecs_patterns.ApplicationLoadBalancedFargateService(
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
                environment=runtime_variables,
                secrets=runtime_secrets,
                task_role=task_role,
            ),
            public_load_balancer=True,
            certificate=certificate,
            redirect_http=True,
            health_check_grace_period=Duration.minutes(5),
        )

        runtime_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200",
        )

        self.load_balancer = runtime_service.load_balancer
