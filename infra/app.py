#!/usr/bin/env python3
import os

import aws_cdk as cdk
import Tags
from aspects.tagging import ConfigTaggingAspect
from config import Config
from stacks.compute import ComputeStack
from stacks.network import NetworkStack
from stacks.runtime import RuntimeStack
from stacks.storage import StorageStack
from stacks.user_management import UserManagementStack

app = cdk.App()
config = Config(
    os.getenv(
        "PROJECT_NAME", os.path.basename(os.path.dirname(os.path.dirname(__file__)))
    ),
    os.getenv("ENVIRONMENT_NAME", "no-env"),
    cdk.Environment(
        account=os.getenv("AWS_ACCOUNT"),
        region=os.getenv("AWS_REGION"),
    ),
)
# cdk.Aspects.of(app).add(ConfigTaggingAspect(config))
for attribute in config.__dict__:
    if not attribute.startswith("_"):
        Tags.of(app).add(attribute, getattr(config, attribute))

user_management_stack = UserManagementStack(app, config)
network_stack = NetworkStack(app, config)

compute_stack = ComputeStack(app, config, vpc=network_stack.vpc_constrcut.vpc)
compute_stack.add_dependency(network_stack)

storage_stack = StorageStack(app, config, vpc=network_stack.vpc_constrcut.vpc)
storage_stack.add_dependency(network_stack)

runtime_stack = RuntimeStack(
    app,
    config,
    certificate=network_stack.cert_construct.certificate,
    hosted_zone=network_stack.cert_construct.hosted_zone,
    vpc=network_stack.vpc_constrcut.vpc,
    db_instance=storage_stack.rds_construct.db_instance,
)
runtime_stack.add_dependency(network_stack)
runtime_stack.add_dependency(compute_stack)
runtime_stack.add_dependency(storage_stack)

app.synth()
