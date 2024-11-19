#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.core import CoreStack
from stacks.cluster import ClusterStack
from stacks.database import DatabaseStack
from stacks.app import AppStack
from stacks.auth import AuthStack

app = cdk.App()

core_stack = CoreStack(
    app, "CoreStack", env=cdk.Environment(account="140465999057", region="us-east-1")
)

auth_stack = AuthStack(
    app, "AuthStack", env=cdk.Environment(account="140465999057", region="us-east-1")
)

cluster_stack = ClusterStack(
    app,
    "ClusterStack",
    vpc=core_stack.vpcConstruct.vpc,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)

database_stack = DatabaseStack(
    app,
    "DatabaseStack",
    vpc=core_stack.vpcConstruct.vpc,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)


app_stack = AppStack(
    app,
    "AppStack",
    cluster=cluster_stack.clusterConstruct.cluster,
    certificate=core_stack.certConstruct.certificate,
    hosted_zone=core_stack.certConstruct.hosted_zone,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)

app.synth()
