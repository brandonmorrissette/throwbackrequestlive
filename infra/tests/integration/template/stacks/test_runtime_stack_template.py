# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest
from aws_cdk import App
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3

from infra.config import Config
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs


@pytest.fixture(scope="module")
def stack(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    app: App,
    config: Config,
    vpc: ec2.IVpc,
    certificate: acm.ICertificate,
    policy: iam.ManagedPolicy,
    cluster: ecs.Cluster,
    bucket: s3.IBucket,
    db_instance: rds.IDatabaseInstance,
    gateway_security_group: ec2.ISecurityGroup,
) -> RuntimeStack:
    return RuntimeStack(
        app,
        # pylint: disable=duplicate-code
        RuntimeStackArgs(
            config,
            vpc=vpc,
            certificate=certificate,
            policy=policy,
            cluster=cluster,
            bucket=bucket,
            db_instance=db_instance,
            gateway_security_group=gateway_security_group,
        ),
    )


def test_runtime_service_resources(services: Mapping[str, Any]) -> None:
    assert len(services) == 1


def test_route53_resources(record_sets: Mapping[str, Any]) -> None:
    assert len(record_sets) == 4
