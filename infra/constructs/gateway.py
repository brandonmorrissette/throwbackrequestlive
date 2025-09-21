"""
This module defines the GatewayConstruct class, which sets up the API Gateway and its associated resources.
"""
from aws_cdk import Duration, BundlingOptions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk import aws_apigatewayv2_integrations as integrations

from infra.constructs.construct import Construct, ConstructArgs
from infra.stacks.stack import Stack
from infra.config import Config


class GatewayConstructArgs(ConstructArgs):
    """
    Arguments for the GatewayConstruct.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.IVpc): The VPC in which the API Gateway is deployed.
        certificate (acm.ICertificate | None): The SSL certificate for the custom domain.
    """

    def __init__(
        self,
        config: Config,
        vpc: ec2.IVpc,
        domain_name: apigwv2.IDomainName,
        uid: str = "gateway",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc
        self.domain_name = domain_name


class GatewayConstruct(Construct):
    """
    This construct sets up the API Gateway and its associated resources.
    """
    def __init__(self, scope: Stack, args: GatewayConstructArgs) -> None:
        super().__init__(scope, ConstructArgs(args.config, args.uid, args.prefix))

        self.security_group = ec2.SecurityGroup(
            self,
            f"{args.config.project_name}-{args.config.environment_name}-gateway-lambda-sg",
            vpc=args.vpc,
            allow_all_outbound=True,
        )

        lambda_role = iam.Role(
            self,
            f"{args.config.project_name}-gateway-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )

        code = _lambda.Code.from_asset("infra/lambda/gateway", 
            bundling=BundlingOptions(
                image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ]
            ),
        )

        lambda_fn = _lambda.Function(
            self,
            f"{args.config.project_name}-runtime-proxy-lambda",
            function_name=f"{args.config.project_name}-{args.config.environment_name}-runtime-proxy-lambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=code,
            role=lambda_role,
            vpc=args.vpc,
            security_groups=[self.security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(30),
        )

        lambda_fn.add_environment(
            "FARGATE_URL",
            f"http://runtime.{args.config.project_name}-{args.config.environment_name}.local:5000"
        )

        integration = integrations.HttpLambdaIntegration(
            f"{args.config.project_name}-lambda-integration",
            lambda_fn,
            payload_format_version=apigwv2.PayloadFormatVersion.VERSION_2_0,
        )

        apigwv2.HttpApi(
            self,
            f"{args.config.project_name}-http-api",
            default_integration=integration,
            default_domain_mapping=apigwv2.DomainMappingOptions(
                domain_name=args.domain_name
            ),
        )
