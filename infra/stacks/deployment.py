"""
This module defines the DeploymentStack class,
which sets up the resources needed only during deployment of the application.

These resources will be destroyed after the deployment is complete.
"""

from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_rds as rds
from constructs import Construct

from infra.config import Config
from infra.deployment.sql.construct import (
    SqlDeploymentConstruct,
    SqlDeploymentConstructArgs,
)
from infra.deployment.superuser.construct import (
    SuperUserConstruct,
    SuperUserConstructArgs,
)
from infra.stacks.stack import Stack, StackArgs


class DeploymentStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    A class that defines args for the DeploymentStack class.

    Attributes:
        config (Config): Configuration object.
        vpc (ec2.Vpc): The VPC in which to create the storage resources.
        security_group (ec2.ISecurityGroup): The security group for the resources.
        cluster (ecs.ICluster): The ECS cluster in which to create the resources.
        db_instance (rds.IDatabaseInstance): The RDS database instance.
        user_pool_id (str): The ID of the Cognito user pool.
        subnet (ec2.ISubnet): The subnet in which to create the resources.
        uid (str): The ID of the stack.
            Defaults to "storage".
        prefix (str): The prefix for the stack name.
            Defaults to "{config.project_name}-{config.environment_name}-".
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: Config,
        vpc: ec2.Vpc,
        security_group: ec2.ISecurityGroup,
        cluster: ecs.ICluster,
        db_instance: rds.IDatabaseInstance,
        user_pool_id: str,
        subnet: ec2.ISubnet,
        uid: str = "deployment",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)
        self.vpc = vpc
        self.subnet = subnet
        self.security_group = security_group
        self.cluster = cluster
        self.db_instance = db_instance
        self.user_pool_id = user_pool_id


class DeploymentStack(Stack):
    """
    This stack sets up the resources needed only during deployment of the application.

    These resources will be destroyed after the deployment is complete.
    """

    def __init__(
        self,
        scope: Construct,
        args: DeploymentStackArgs,
    ) -> None:
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        ec2.InterfaceVpcEndpoint(
            self,
            "EcrEndpoint",
            vpc=args.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            removal_policy=RemovalPolicy.DESTROY,
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "SsmEndpoint",
            vpc=args.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            removal_policy=RemovalPolicy.DESTROY,
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "EcrDockerEndpoint",
            vpc=args.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            removal_policy=RemovalPolicy.DESTROY,
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "SecretsManagerEndpoint",
            vpc=args.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            removal_policy=RemovalPolicy.DESTROY,
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "CloudWatchLogsEndpoint",
            vpc=args.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Deployment Task Constructs
        sql_task_construct = SqlDeploymentConstruct(
            self,
            SqlDeploymentConstructArgs(
                config=args.config,
                db_instance=args.db_instance,
            ),
        )

        superuser_task_construct = SuperUserConstruct(
            self,
            SuperUserConstructArgs(
                config=args.config,
                user_pool_id=args.user_pool_id,
            ),
        )

        # CFN Outputs
        CfnOutput(
            self,
            "securitygroupid",
            value=args.security_group.security_group_id,
        )

        CfnOutput(
            self,
            "subnetid",
            value=args.subnet.subnet_id,
        )

        CfnOutput(self, "ecsclustername", value=args.cluster.cluster_name)

        CfnOutput(
            self,
            "sqltaskdefinitionarn",
            value=sql_task_construct.task_definition.task_definition_arn,
        )

        CfnOutput(
            self,
            "superusertaskdefinitionarn",
            value=superuser_task_construct.task_definition.task_definition_arn,
        )
