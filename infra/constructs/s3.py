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

        ssm.StringParameter(
            self,
            "bucket-name-parameter",
            parameter_name=f"/{config.project_name}-{config.environment_name}/bucket-name",
            string_value=self.bucket.bucket_name,
        )
