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
    app, ComputeStackArgs(config, vpc=network_stack.vpc_constrcut.vpc)
)
compute_stack.add_dependency(network_stack)

storage_stack = StorageStack(
    app, StorageStackArgs(config, vpc=network_stack.vpc_constrcut.vpc)
)
storage_stack.add_dependency(network_stack)

runtime_stack = RuntimeStack(
    app,
    RuntimeStackArgs(
        config, user_management_stack, network_stack, compute_stack, storage_stack
    ),
)

runtime_stack.add_dependency(user_management_stack)
runtime_stack.add_dependency(network_stack)
runtime_stack.add_dependency(compute_stack)
runtime_stack.add_dependency(storage_stack)

app.synth()
