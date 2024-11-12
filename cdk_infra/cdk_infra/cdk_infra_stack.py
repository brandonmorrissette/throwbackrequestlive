from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam
)
from constructs import Construct

class ThrowbackRequestLiveStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "ThrowbackRequestLiveVpc", max_azs=2)

        cluster = ecs.Cluster(self, "ThrowbackRequestLiveCluster", vpc=vpc)

        repository = ecr.Repository(self, "ThrowbackRequestLiveRepository")

        task_definition = ecs.FargateTaskDefinition(
            self, "ThrowbackRequestLiveTaskDef",
            memory_limit_mib=512,
            cpu=256
        )

        task_definition.add_to_execution_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability"
                ],
                resources=[repository.repository_arn]
            )
        )

        container = task_definition.add_container(
            "ThrowbackRequestLiveContainer",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ThrowbackRequestLive")
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=5000)
        )

        service = ecs.FargateService(
            self, "ThrowbackRequestLiveService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            assign_public_ip=True,
            security_groups=[ec2.SecurityGroup(self, "ThrowbackRequestLiveSG", vpc=vpc, allow_all_outbound=True)]
        )

