from aws_cdk import aws_ecs as ecs, aws_logs
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import Duration
from constructs import Construct


class RuntimeEcsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, cluster, certificate) -> None:
        super().__init__(scope, id)

        docker_image = ecr_assets.DockerImageAsset(
            self, "throwback-request-live-image",
            directory="."
        )

        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "fargate-service",
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
                )
            ),
            public_load_balancer=True,
            certificate=certificate,
            redirect_http=True,
            health_check_grace_period=Duration.minutes(5)
        )

        self.fargate_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200"
        )
