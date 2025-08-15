"""
This module defines a construct for setting up
an Application Load Balancer (ALB) in a VPC using AWS CDK.

Classes:
    - LoadBalancerConstructArgs: Arguments for LoadBalancerConstruct.
    - LoadBalancerConstruct: A construct that sets up an ALB in a VPC.
"""

from aws_cdk import RemovalPolicy
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class LoadBalancerConstructArgs(ConstructArgs):
    """
    Arguments for LoadBalancerConstruct.

    Attributes:
        config (Config): The configuration object.
        vpc (ec2.IVpc): The VPC where the ALB will be deployed.
        certificate (acm.Certificate): The ACM certificate for HTTPS.
        uid (str): A unique identifier for the construct.
        prefix (str): A prefix for resource names.
    """

    def __init__(
        self,
        config: Config,
        vpc: ec2.IVpc,
        certificate: acm.Certificate,
        uid: str = "load-balancer",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc
        self.certificate = certificate


class LoadBalancerConstruct(Construct):
    """
    A construct that sets up an Application Load Balancer (ALB) in a VPC.

    Attributes:
        load_balancer (elbv2.ApplicationLoadBalancer): The ALB instance.
    """

    def __init__(self, scope: Stack, args: LoadBalancerConstructArgs) -> None:
        """
        Initializes the LoadBalancerConstruct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            args (LoadBalancerConstructArgs): The arguments for the construct.
        """
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        log_bucket = s3.Bucket(
            self,
            "alb-log-bucket",
            bucket_name=f"{args.config.project_name}-{args.config.environment_name}-load-balancer-log-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )

        log_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("logdelivery.elb.amazonaws.com")],
                actions=["s3:PutObject"],
                resources=[
                    f"{log_bucket.bucket_arn}/AWSLogs/{args.config.cdk_environment.account}/*"
                ],
                conditions={
                    "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                },
            )
        )

        self.load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            f"{args.config.project_name}-{args.config.environment_name}-alb",
            vpc=args.vpc,
            internet_facing=True,
            ip_address_type=elbv2.IpAddressType.IPV4,
        )

        self.load_balancer.log_access_logs(
            log_bucket,
            prefix="streams",
        )
