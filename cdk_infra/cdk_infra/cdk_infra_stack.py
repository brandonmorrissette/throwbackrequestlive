from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
)
from constructs import Construct

class ThrowbackRequestLiveStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "ThrowbackRequestLiveVpc", max_azs=2)
        cluster = ecs.Cluster(self, "ThrowbackRequestLiveCluster", vpc=vpc)

        repository = ecr.Repository(self, "ThrowbackRequestLiveRepository")

        certificate = acm.Certificate(
            self, 
            "SiteCertificate",
            domain_name="www.throwbackrequestlive.com",
            validation=acm.CertificateValidation.from_dns()
        )


        alb = elbv2.ApplicationLoadBalancer(
            self, 
            "ThrowbackRequestLiveALB",
            vpc=vpc,
            internet_facing=True
        )

        listener = alb.add_listener(
            "HttpsListener",
            port=443,
            certificates=[certificate]
        )

        target_group = listener.add_targets(
            "ECS",
            port=80,
            targets=[ecs.EcsService(self, "MyService", cluster=cluster, task_definition=task_definition)]
        )

        alb.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Allow HTTPS")

        hosted_zone = route53.HostedZone.from_lookup(
            self, 
            "HostedZone",
            domain_name="throwbackrequestlive.com"
        )


        route53.ARecord(
            self,
            "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(route53_targets.LoadBalancerTarget(alb)),
            record_name="www" 
        )
