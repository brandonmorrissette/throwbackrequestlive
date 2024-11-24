from aws_cdk import aws_ec2 as ec2, aws_rds as rds, Duration
from constructs import Construct


class RdsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc, project_name: str) -> None:
        super().__init__(scope, id)

        rds_security_group = ec2.SecurityGroup(self, "RDSSecurityGroup", vpc=vpc)
        rds_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(5432), "Allow ECS to access RDS"
        )

        self.db_instance = rds.DatabaseInstance(
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
            database_name="throwbackrequestlive",
            security_groups=[rds_security_group],
            instance_identifier=f"{project_name}-rds-instance"
        )
