"""
This module contains the RuntimeEcsConstruct class, which sets up an ECS Fargate service
with a load balancer, task definition, and secrets management.

Classes:
    RuntimeEcsConstruct: A construct that sets up an ECS Fargate service.

Usage example:
    runtime_ecs_construct = RuntimeEcsConstruct(scope, config, certificate, 
        policy, cluster, runtime_variables, runtime_secrets)
"""

from dataclasses import dataclass

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


@dataclass
class RuntimeEcsConstructArgs:
    """
    A class that defines properties for the RuntimeEcsConstruct class.

    Attributes:
        certificate (acm.Certificate): The ACM certificate for the load balancer.
        policy (iam.ManagedPolicy): The IAM managed policy for the task role.
        cluster (ecs.Cluster): The ECS cluster.
        runtime_variables (dict): The environment variables for the ECS task.
        runtime_secrets (dict): The secrets for the ECS task.
    """

    certificate: acm.Certificate
    policy: iam.ManagedPolicy
    cluster: ecs.Cluster
    runtime_variables: dict
    runtime_secrets: dict


class RuntimeEcsConstruct(Construct):
    """
    A construct that sets up an ECS Fargate service.

    Attributes:
        load_balancer: The load balancer for the ECS service.

    Methods:
        __init__: Initializes the RuntimeEcsConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        config: Config,
        args: RuntimeEcsConstructArgs,
        construct_id: str | None = None,
    ) -> None:
        """
        Initializes the RuntimeEcsConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): Configuration object.
            certificate (acm.Certificate): The ACM certificate for the load balancer.
            policy (iam.ManagedPolicy): The IAM managed policy for the task role.
            cluster (ecs.Cluster): The ECS cluster.
            runtime_variables (dict): The environment variables for the ECS task.
            runtime_secrets (dict): The secrets for the ECS task.
            construct_id (str, optional): The ID of the construct.
                Defaults to f"{config.project_name}-{config.environment_name}-runtime-ecs".
        """
        super().__init__(scope, config, construct_id, "runtime-ecs")

        jwt_secret = secretsmanager.Secret(
            self,
            "JWTSecret",
            description="JWT secret for secure token generation",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=32, exclude_punctuation=True
            ),
        )

        args.runtime_secrets["JWT_SECRET_KEY"] = ecs.Secret.from_secrets_manager(
            jwt_secret
        )

        task_role = iam.Role(
            self,
            "RuntimeTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                args.policy,
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

        self.runtime_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "runtime-service",
            cluster=args.cluster,
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
                environment=args.runtime_variables,
                secrets=args.runtime_secrets,
                task_role=task_role,
            ),
            public_load_balancer=True,
            certificate=args.certificate,
            redirect_http=True,
            health_check_grace_period=Duration.minutes(5),
        )

        self.runtime_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200",
        )
