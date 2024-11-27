#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.compute import ComputeStack
from stacks.environment_setup import EnvironmentSetupStack
from stacks.network import NetworkStack
from stacks.runtime import RuntimeStack
from stacks.storage import StorageStack
from stacks.user_management import UserManagementStack

app = cdk.App()
project_name = os.getenv("PROJECT_NAME", os.path.basename(os.path.dirname(os.path.dirname(__file__))))
environment_name = os.getenv("ENVIRONMENT_NAME", "no-env")

tags = {
    "project_name": project_name,
    "environment_name": environment_name
}

env = cdk.Environment(
    account=os.getenv("AWS_ACCOUNT", "140465999057"), 
    region=os.getenv("AWS_REGION", "us-east-1")
)

def apply_tags(resource, tags):
    for key, value in tags.items():
        cdk.Tags.of(resource).add(key, value)

apply_tags(app, {key: value for key, value in vars(env).items() if isinstance(value, str)})
apply_tags(app, tags)

core_stack = NetworkStack(
    app, 
    f"{project_name}-network-stack-{environment_name}",
    env=env
)
apply_tags(core_stack, tags=tags)

compute_stack = ComputeStack(
    app,
    f"{project_name}-compute-stack-{environment_name}",
    env=env,
    vpc=core_stack.vpc_constrcut.vpc,
    
)
apply_tags(compute_stack, tags=tags)

storage_stack = StorageStack(
    app,
    f"{project_name}-storage-stack-{environment_name}",
    env=env,
    vpc=core_stack.vpc_constrcut.vpc,
    project_name=project_name
    
)
apply_tags(storage_stack,tags=tags)

user_stack = UserManagementStack(
    app, 
    f"{project_name}-user-management-stack-{environment_name}", 
    env=env, 
    rds=storage_stack.rds_construct.db_instance, 
    project_name=project_name
)
apply_tags(user_stack, tags=tags)

app_stack = RuntimeStack(
    app,
    f"{project_name}-runtime-stack-{environment_name}",
    env=env,
    cluster=compute_stack.cluster_construct.cluster,
    certificate=core_stack.cert_construct.certificate,
    hosted_zone=core_stack.cert_construct.hosted_zone,
)
apply_tags(app_stack, tags=tags)

environment_setup_stack = EnvironmentSetupStack(
    app,
    f"{project_name}-environment-setup-stack-{environment_name}",
    env=env,
    cluster=compute_stack.cluster_construct.cluster,
    rds_secret=storage_stack.rds_construct.db_instance.secret,
    project_name=project_name,
)
apply_tags(environment_setup_stack, tags=tags)

app.synth()
