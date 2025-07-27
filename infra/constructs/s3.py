"""
This module contains the S3Construct class, which sets up an S3 bucket
with appropriate configurations and permissions.

Classes:
    S3Construct: A construct that sets up an S3 bucket.

Usage example:
    s3_construct = S3Construct(scope, config)
"""

from aws_cdk import RemovalPolicy
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm

from infra.config import Config
from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack


class S3Construct(Construct):
    """
    A construct that sets up an S3 bucket.

    Attributes:
        bucket: The S3 bucket.

    Methods:
        __init__: Initializes the S3Construct with the given parameters.
    """

    def __init__(
        self,
        scope: Stack,
        config: Config,
        load_balancer: elbv2.IApplicationLoadBalancer,
        uid: str = "s3",
        prefix: str = "",
    ) -> None:
        """
        Initializes the S3Construct with the given parameters.

        Args:
            scope (Stack): The parent stack.
            config (Config): The configuration object.
            uid (str): The ID of the construct.
                Defaults to "s3".
            prefix (str): The prefix for resource names.
                Defaults to f"{config.project_name}-{config.environment_name}".
        """
        super().__init__(scope, ConstructArgs(config, uid, prefix))

        bucket_name = (
            f"{config.project_name.lower() if config.project_name else None}"
            f"-{config.environment_name.lower() if config.environment_name else None}-bucket"
        )

        self.bucket = s3.Bucket(
            self,
            "s3-bucket",
            bucket_name=bucket_name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[self.bucket.bucket_arn + "/*"],
                principals=[iam.ServicePrincipal("delivery.logs.amazonaws.com")],
            )
        )

        self.bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetBucketAcl"],
                principals=[
                    iam.ServicePrincipal(
                        "logdelivery.elasticloadbalancing.amazonaws.com"
                    )
                ],
                resources=[self.bucket.bucket_arn],
            )
        )

        self.bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                principals=[
                    iam.ServicePrincipal(
                        "logdelivery.elasticloadbalancing.amazonaws.com"
                    )
                ],
                resources=[
                    self.bucket.arn_for_objects(
                        f"{prefix}AWSLogs/{config.cdk_environment.account}/*"
                    )
                ],
                conditions={
                    "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                },
            )
        )

        load_balancer.log_access_logs(
            self.bucket,
        )

        ssm.StringParameter(
            self,
            "bucket-name-parameter",
            parameter_name=f"/{config.project_name}-{config.environment_name}/bucket-name",
            string_value=self.bucket.bucket_name,
        )
