# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import App
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_route53 as route53

from infra.config import Config
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs


@pytest.fixture(scope="module")
def stack(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    app: App,
    config: Config,
    vpc: ec2.IVpc,
    certificate: acm.ICertificate,
    hosted_zone: route53.IHostedZone,
    policy: iam.ManagedPolicy,
    cluster: ecs.Cluster,
    db_instance: rds.IDatabaseInstance,
    cache_cluster: elasticache.CfnCacheCluster,
    load_balancer: elbv2.IApplicationLoadBalancer,
) -> RuntimeStack:
    return RuntimeStack(
        app,
        RuntimeStackArgs(
            config,
            vpc=vpc,
            certificate=certificate,
            hosted_zone=hosted_zone,
            policy=policy,
            cluster=cluster,
            db_instance=db_instance,
            cache_cluster=cache_cluster,
            load_balancer=load_balancer,
        ),
    )


def test_runtime_service_resources(services: Mapping[str, Any]) -> None:
    assert len(services) == 1


def test_route53_resources(record_sets: Mapping[str, Any]) -> None:
    assert len(record_sets) == 4
