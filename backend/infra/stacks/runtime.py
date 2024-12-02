from aws_cdk import Stack
from constructs import Construct
from constructs.route_53 import Route53Construct
from constructs.runtime_ecs import RuntimeEcsConstruct


class RuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        env,
        project_name: str,
        certificate: str,
        hosted_zone: str,
        vpc,
        **kwargs
    ):
        super().__init__(scope, id, env=env, **kwargs)
        fargate_service = RuntimeEcsConstruct(
            self,
            "runtime-ecs",
            project_name=project_name,
            certificate=certificate,
            vpc=vpc,
            env=env,
        ).runtime_service

        Route53Construct(
            self,
            "route-53",
            hosted_zone=hosted_zone,
            load_balancer=fargate_service.load_balancer,
        )
