from aws_cdk import Stack, aws_ecs as ecs, aws_ec2 as ec2, aws_iam as iam, CfnOutput, aws_secretsmanager as secretsmanager
from constructs import Construct

class EnvironmentSetupStack(Stack):
    def __init__(self, scope: Construct, id: str, cluster: ecs.Cluster, rds_secret: secretsmanager.ISecret, user_pool_id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        cognito_secrets = secretsmanager.Secret.from_secret_name_v2(self, "cognito-secrets", "cognito_secrets")

        sql_task_definition = ecs.FargateTaskDefinition(self, "sql-task-definition",
            memory_limit_mib=512,
            cpu=256
        )
        sql_task_definition.add_container("sql-container",
            image=ecs.ContainerImage.from_registry("amazonlinux"),
            secrets={
                "DB_HOST": ecs.Secret.from_secrets_manager(rds_secret, "host"),
                "DB_USER": ecs.Secret.from_secrets_manager(rds_secret, "username"),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(rds_secret, "password")
            },
            command=["sh", "-c", "for file in /schema/*.sql; do psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/throwbackrequestlive -f $file; done"],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="sql-deployment")
        )
        security_group = ec2.SecurityGroup(self, "task-security-group",
            vpc=cluster.vpc,
            description="Allow ECS tasks to communicate with RDS",
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL access")
        
        CfnOutput(self, "security-group-id", value=security_group.security_group_id)
        CfnOutput(self, "sql-task-definition-arn", value=sql_task_definition.task_definition_arn)
        CfnOutput(self, "ecs-cluster-name", value=cluster.cluster_name)

        superuser_task_definition = ecs.FargateTaskDefinition(self, "superuser-task-definition",
            memory_limit_mib=512,
            cpu=256
        )
        superuser_task_definition.add_container("superuser-container",
            image=ecs.ContainerImage.from_registry("amazonlinux"),
            environment={
                "USER_POOL_ID": user_pool_id,
            },
            command=["sh", "-c", "python /infra/setup/create_superuser.py"],
            logging=ecs.LogDrivers.aws_logs(stream_prefix="superuser-creation")
        )
        CfnOutput(self, "superuser-task-definition-arn", value=superuser_task_definition.task_definition_arn)
