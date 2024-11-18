from aws_cdk import aws_ecs_patterns as ecs_patterns, aws_ecr_assets as ecr_assets, aws_ecs as ecs, aws_logs, Duration
from constructs import Construct


class RuntimeEcsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, cluster, certificate) -> None:
        super().__init__(scope, id)

        docker_image = ecr_assets.DockerImageAsset(
            self, "LocalThrowbackRequestLiveImage",
            directory="."
        )

        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=docker_image.image_uri,
                container_port=5000,
            log_driver=ecs.LogDrivers.aws_logs(
                stream_prefix="ThrowbackRequestLive",
                log_group=aws_logs.LogGroup(
                    self, "LogGroup",
                    retention=aws_logs.RetentionDays.ONE_WEEK
                )
            )

            ),
            public_load_balancer=True,
            certificate=certificate,
            redirect_http=True
        )

        self.fargate_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200"
        )
