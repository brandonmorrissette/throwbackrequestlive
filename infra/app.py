#!/usr/bin/env python3
"""
This module sets up the AWS CDK application and its stacks.

Modules:
    aws_cdk: AWS CDK library.
    aspects.tagging: Custom tagging aspect.
    aws_cdk.Aspects: AWS CDK Aspects.
    config: Configuration module.
    stacks.compute: Compute stack module.
    stacks.network: Network stack module.
    stacks.runtime: Runtime stack module.
    stacks.storage: Storage stack module.
    stacks.user_management: User management stack module.

Usage example:
    python app.py
"""

import os

import aws_cdk as cdk

from infra.config import Config
from infra.stacks.compute import ComputeStack, ComputeStackArgs
from infra.stacks.network import NetworkStack, NetworkStackArgs
from infra.stacks.runtime import RuntimeStack, RuntimeStackArgs
from infra.stacks.storage import StorageStack, StorageStackArgs
from infra.stacks.user_management import UserManagementStack, UserManagementStackArgs

app = cdk.App()
config = Config(
    os.getenv(
        "PROJECT_NAME", os.path.basename(os.path.dirname(os.path.dirname(__file__)))
    ),
    os.getenv("ENVIRONMENT_NAME"),
    cdk.Environment(
        account=os.getenv("AWS_ACCOUNT"),
        region=os.getenv("AWS_REGION"),
    ),
)

user_management_stack = UserManagementStack(app, UserManagementStackArgs(config))
network_stack = NetworkStack(app, NetworkStackArgs(config))

compute_stack = ComputeStack(
    app, ComputeStackArgs(config, vpc=network_stack.vpc_construct.vpc)
)

storage_stack = StorageStack(
    app,
    StorageStackArgs(
        config,
        vpc=network_stack.vpc_construct.vpc,
    ),
)


runtime_stack = RuntimeStack(
    app,
    RuntimeStackArgs(
        config=config,
        vpc=network_stack.vpc_construct.vpc,
        certificate=network_stack.cert_construct.certificate,
        hosted_zone=network_stack.cert_construct.hosted_zone,
        policy=user_management_stack.superuser_construct.policy,
        cluster=compute_stack.cluster_construct.cluster,
        db_credentials_arn=storage_stack.rds_construct.db_instance.secret.secret_arn,
        cache_cluster=storage_stack.cache_construct.cluster,
        load_balancer=network_stack.load_balancer_construct.load_balancer,
    ),
)

app.synth()
