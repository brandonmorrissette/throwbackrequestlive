from aws_cdk import Stack
from config import Config
from constructs import Construct
from constructs.route_53 import Route53Construct
from constructs.runtime_ecs import RuntimeEcsConstruct


class RuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        certificate: str,
        hosted_zone: str,
        db_instance,
        vpc,
    ):
        super().__init__(
            scope,
            f"{config.project_name}-{config.environment_name}-runtime",
            env=config.cdk_environment,
        )
        fargate_service = RuntimeEcsConstruct(
            self,
            "runtime-ecs",
            project_name=config.project_name,
            certificate=certificate,
            vpc=vpc,
            env=config.cdk_environment,
            db_instance=db_instance,
        ).runtime_service

        Route53Construct(
            self,
            "route-53",
            hosted_zone=hosted_zone,
            load_balancer=fargate_service.load_balancer,
        )
