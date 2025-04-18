"""
This module contains the RuntimeEcsConstruct class, which sets up an ECS Fargate service
with a load balancer, task definition, and secrets management.

Classes:
    RuntimeEcsConstruct: A construct that sets up an ECS Fargate service.

Usage example:
    runtime_ecs_construct = RuntimeEcsConstruct(scope, config, certificate,
        policy, cluster, runtime_variables, runtime_secrets)
"""

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class RuntimeConstructArgs(ConstructArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines properties for the RuntimeConstruct class.

    Attributes:
        config: Configuration object.
        certificate (acm.Certificate): The ACM certificate for the load balancer.
        policy (iam.ManagedPolicy): The IAM managed policy for the task role.
        cluster (ecs.Cluster): The ECS cluster.
        runtime_variables (dict): The environment variables for the ECS task.
        runtime_secrets (dict): The secrets for the ECS task.
        uid: Unique identifier for the resource.
            Defaults to runtime.
        prefix: Prefix for resource names.
            Defaults to f"{config.project_name}-{config.environment_name}-".
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        certificate: acm.ICertificate,
        policy: iam.ManagedPolicy,
        cluster: ecs.Cluster,
        db_credentials_arn: str,
        runtime_variables: dict[str, str] | None = None,
        uid: str = "runtime",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.certificate = certificate
        self.policy = policy
        self.cluster = cluster
        self.runtime_variables = runtime_variables
        self.db_credentials_arn = db_credentials_arn


class RuntimeConstruct(Construct):
    """
    A construct that sets up an ECS Fargate service.

    Attributes:
        runtime_service (ecs_patterns.ApplicationLoadBalancedFargateService):
            The ECS Fargate service.

    Methods:
        __init__: Initializes the RuntimeEcsConstruct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        args: RuntimeConstructArgs,
    ) -> None:
        """
        Initializes the RuntimeEcsConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (RuntimeConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        jwt_secret = secretsmanager.Secret(
            self,
            "JWTSecret",
            description="JWT secret for secure token generation",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=32, exclude_punctuation=True
            ),
        )

        policy = iam.ManagedPolicy(
            self,
            "runtime-policy",
            managed_policy_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-runtime-policy",
            # pylint: disable=R0801
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                    ],
                    resources=[
                        jwt_secret.secret_arn,
                        args.db_credentials_arn,
                    ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "ssm:GetParameter",
                    ],
                    resources=[
                        f"arn:aws:ssm:{args.config.cdk_environment.region}:"
                        f"{args.config.cdk_environment.account}:"
                        f"parameter/{args.config.project_name}-{args.config.environment_name}/*"
                    ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:DeleteObject",
                    ],
                    resources=[
                        f"arn:aws:s3:::{args.config.project_name}-"
                        f"{args.config.environment_name}-bucket/*",
                    ],
                ),
            ],
        )

        task_role = iam.Role(
            self,
            "RuntimeTaskRole",
            role_name=f"{args.config.project_name}-"
            f"{args.config.environment_name}-runtime-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                args.policy,
                policy,
            ],
        )

        docker_image = ecr_assets.DockerImageAsset(
            self,
            f"{args.config.project_name}-{args.config.environment_name}-image",
            directory=".",
            exclude=["infra", "infra/*", "cdk.out", "node_modules"],
        )

        log_group = aws_logs.LogGroup(
            self,
            "runtime-log-group",
            log_group_name=f"/{args.config.project_name}-{args.config.environment_name}-runtime",
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        task_image = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            image=ecs.ContainerImage.from_docker_image_asset(docker_image),
            container_port=5000,
            log_driver=ecs.LogDrivers.aws_logs(
                stream_prefix=args.config.project_name, log_group=log_group
            ),
            environment=args.runtime_variables,
            secrets={"JWT_SECRET_KEY": ecs.Secret.from_secrets_manager(jwt_secret)},
            task_role=task_role,
        )

        self.runtime_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "runtime-service",
            cluster=args.cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=task_image,
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
