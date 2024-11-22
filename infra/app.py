#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.core import CoreStack
from stacks.cluster import ClusterStack
from stacks.storage import StorageStack
from stacks.runtime import RuntimeStack
from stacks.setup import SetupStack

app = cdk.App()
project_name = os.getenv("PROJECT_NAME")
environment_name = os.getenv("ENVIRONMENT_NAME", "Production")

env = cdk.Environment(
    account=os.getenv("AWS_ACCOUNT", "140465999057"), 
    region=os.getenv("AWS_REGION", "us-east-1")
)

core_stack = CoreStack(
    app, 
    f"{project_name}-CoreStack-{environment_name}",
    env=env
)

cluster_stack = ClusterStack(
    app,
    f"{project_name}-ClusterStack-{environment_name}",
    env=env,
    vpc=core_stack.vpcConstruct.vpc,
    
)

database_stack = StorageStack(
    app,
    f"{project_name}-StorageStack-{environment_name}",
    env=env,
    vpc=core_stack.vpcConstruct.vpc,
    
)

setup_stack = SetupStack(
    app, 
    f"{project_name}-SetupStack-{environment_name}", 
    env=env, 
    rds=database_stack.rdsConstruct.db_instance, 
    project_name=project_name
)

app_stack = RuntimeStack(
    app,
    f"{project_name}-RuntimeStack-{environment_name}",
    env=env,
    cluster=cluster_stack.clusterConstruct.cluster,
    certificate=core_stack.certConstruct.certificate,
    hosted_zone=core_stack.certConstruct.hosted_zone,
)

app.synth()
