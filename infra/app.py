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
    vpc_id=core_stack.vpc_output,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)

database_stack = DatabaseStack(
    app,
    "DatabaseStack",
    vpc=core_stack.vpc,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)


app_stack = AppStack(
    app,
    "AppStack",
    cluster_arn=cluster_stack.cluster_arn,
    certificate_arn=core_stack.certificate_output,
    hosted_zone_id=core_stack.hosted_zone_output,
    env=cdk.Environment(account="140465999057", region="us-east-1"),
)

app.synth()
