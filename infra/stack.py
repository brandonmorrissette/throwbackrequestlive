from aws_cdk import Stack
from constructs import Construct
from constructs.vpc import VpcConstruct
from constructs.cluster import ClusterConstruct
from constructs.cert import CertConstruct
from constructs.runtime_ecs import RuntimeEcsConstruct
from constructs.route_53 import Route53Construct
from constructs.rds import RdsConstruct
from constructs.cognito import CognitoConstruct
from constructs.superuser import SuperuserConstruct
from constructs.deployment_ec2 import DeploymentEc2Construct


class ThrowbackRequestLiveStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = VpcConstruct(self, "Vpc").vpc

        cluster = ClusterConstruct(self, "Cluster", vpc).cluster

        cert = CertConstruct(self, "Cert")
        hosted_zone = cert.hosted_zone
        certificate = cert.certificate

        fargate_service = RuntimeEcsConstruct(self, "RuntimeEcs", cluster, certificate).fargate_service

        Route53Construct(self, "Route53", hosted_zone, fargate_service.load_balancer)

        RdsConstruct(self, "Rds", vpc).db_instance

        CognitoConstruct(self, "Cognito")

        SuperuserConstruct(self, "Superuser")

        DeploymentEc2Construct(self, "DeploymentEc2", vpc)
