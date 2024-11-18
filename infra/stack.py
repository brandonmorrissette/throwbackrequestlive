from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_ecr_assets as ecr_assets,
    aws_rds as rds,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
    aws_cognito as cognito,
    aws_logs,
    Duration,
    CfnOutput,
    Size,
    Tags,
)

from constructs import Construct
from pathlib import Path
import os


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

        rds_security_group = ec2.SecurityGroup(self, "RDSSecurityGroup", vpc=vpc)
        rds_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(5432), "Allow ECS to access RDS"
        )

        db_instance = rds.DatabaseInstance(
            self, "RDSInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            credentials=rds.Credentials.from_generated_secret("db_master_user"),
            allocated_storage=20,
            multi_az=False,
            publicly_accessible=False,
            backup_retention=Duration.days(7),
            database_name="throwback",
            security_groups=[rds_security_group]
        )

        CfnOutput(
            self, "RDSEndpoint",
            value=db_instance.db_instance_endpoint_address,
            description="RDS Endpoint"
        )

        user_pool = cognito.UserPool(
            self, "UserPool",
            self_sign_up_enabled=False,
            user_pool_name="UserPool",
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
        )

        app_client = user_pool.add_client(
            "UserPoolAppClient",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True
            )
        )

        admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Admin",
            user_pool_id=user_pool.user_pool_id
        )

        CfnOutput(
            self, "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )

        CfnOutput(
            self, "AppClientId",
            value=app_client.user_pool_client_id,
            description="Cognito App Client ID"
        )

        ec2_role = iam.Role(
            self, "EC2InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSFullAccess"),
            ]
        )

        ec2_security_group = ec2.SecurityGroup(self, "EC2SecurityGroup", vpc=vpc)
        ec2_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(22), "Allow SSH within VPC"
        )
        ec2_security_group.add_egress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.all_traffic(), "Allow outbound traffic"
        )

        deployment_ec2_instance = ec2.Instance(
            self, "DeploymentInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            role=ec2_role,
            security_group=ec2_security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        Tags.of(deployment_ec2_instance).add("Name", "DeploymentInstance")

        deployment_ebs_volume = ec2.Volume(
            self,
            "DeploymentVolume",
            availability_zone=vpc.availability_zones[0],
            size=Size.gibibytes(1),
            volume_type=ec2.EbsDeviceVolumeType.GP2
        )

        ec2.CfnVolumeAttachment(
            self,
            "VolumeAttachment",
            instance_id=deployment_ec2_instance.instance_id,
            volume_id=deployment_ebs_volume.volume_id,
            device="/dev/xvdf"
        )

        schema_dir_asset = s3_assets.Asset(
            self,
            "SchemaDirAsset",
            path=str(Path(__file__).parent.parent / "schema")
        )

        schema_dir_asset.grant_read(deployment_ec2_instance.role)

        deployment_ec2_instance.add_user_data(
            "yum update -y",
            "amazon-linux-extras enable postgresql14",
            "yum install -y postgresql unzip aws-cli",
            "mkfs -t ext4 /dev/xvdf",
            "mkdir /mnt/schema",
            "mount /dev/xvdf /mnt/schema",
            "echo '/dev/xvdf /mnt/schema ext4 defaults 0 0' >> /etc/fstab",
            f"aws s3 cp {schema_dir_asset.s3_object_url} /mnt/schema/schema.zip",
            "unzip /mnt/schema/schema.zip -d /mnt/schema/"
        )
