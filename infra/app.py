#!/usr/bin/env python3
import aws_cdk as cdk
from infra.stack import ThrowbackRequestLiveStack

app = cdk.App()
ThrowbackRequestLiveStack(
    app, 
    "ThrowbackRequestLiveStack",
    env=cdk.Environment(
        account="140465999057",
        region="us-east-1"
    )
)

app.synth()
