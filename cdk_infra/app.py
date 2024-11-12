#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_infra.cdk_infra_stack import ThrowbackRequestLiveStack


app = cdk.App()
ThrowbackRequestLiveStack(app, "ThrowbackRequestLiveStack")
app.synth()
