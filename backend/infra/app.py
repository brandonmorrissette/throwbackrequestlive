#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.network import NetworkStack
from stacks.compute import ComputeStack
from stacks.storage import StorageStack
from stacks.runtime import RuntimeStack
from stacks.user import UserStack
from stacks.environment_setup_stack import EnvironmentSetupStack

app = cdk.App()
project_name = os.getenv("PROJECT_NAME")
environment_name = os.getenv("ENVIRONMENT_NAME", "Production")

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
    f"{project_name}-NetworkStack-{environment_name}",
    env=env
)
apply_tags(core_stack, tags=tags)

compute_stack = ComputeStack(
    app,
    f"{project_name}-ComputeStack-{environment_name}",
    env=env,
    vpc=core_stack.vpcConstruct.vpc,
    
)
apply_tags(compute_stack, tags=tags)

storage_stack = StorageStack(
    app,
    f"{project_name}-StorageStack-{environment_name}",
    env=env,
    vpc=core_stack.vpcConstruct.vpc,
    project_name=project_name
    
)
apply_tags(storage_stack,tags=tags)

user_stack = UserStack(
    app, 
    f"{project_name}-UserStack-{environment_name}", 
    env=env, 
    rds=storage_stack.rdsConstruct.db_instance, 
    project_name=project_name
)
apply_tags(user_stack, tags=tags)

app_stack = RuntimeStack(
    app,
    f"{project_name}-RuntimeStack-{environment_name}",
    env=env,
    cluster=compute_stack.clusterConstruct.cluster,
    certificate=core_stack.certConstruct.certificate,
    hosted_zone=core_stack.certConstruct.hosted_zone,
)
apply_tags(app_stack, tags=tags)

environment_setup_stack = EnvironmentSetupStack(
    app,
    f"{project_name}-EnvironmentSetupStack-{environment_name}",
    env=env,
    cluster=compute_stack.clusterConstruct.cluster,
    rds_secret=storage_stack.rdsConstruct.db_instance.secret,
    user_pool_id=user_stack.cognitoConstruct.user_pool_id,
)
apply_tags(environment_setup_stack, tags=tags)

app.synth()
