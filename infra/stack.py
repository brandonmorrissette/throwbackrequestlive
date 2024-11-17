from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_ecr_assets as ecr_assets,
    aws_logs,
    Duration,
    CfnOutput
)
from constructs import Construct

class ThrowbackRequestLiveStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "ThrowbackRequestLiveVPC", max_azs=2)

        cluster = ecs.Cluster(self, "ThrowbackRequestLiveCluster", vpc=vpc)

        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="throwbackrequestlive.com"
        )

        certificate = acm.Certificate(
            self, "SiteCertificate",
            domain_name="throwbackrequestlive.com",
            subject_alternative_names=["www.throwbackrequestlive.com"],
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        docker_image = ecr_assets.DockerImageAsset(
            self, "LocalThrowbackRequestLiveImage",
            directory="."
        )

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(docker_image),
                container_port=5000,
                log_driver=ecs.LogDriver.aws_logs(
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

        fargate_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_http_codes="200"
        )

        route53.ARecord(
            self, "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(fargate_service.load_balancer))
        )

        route53.ARecord(
            self, "AliasRecordWWW",
            zone=hosted_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(fargate_service.load_balancer))
        )

        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Public DNS of the Load Balancer"
        )
