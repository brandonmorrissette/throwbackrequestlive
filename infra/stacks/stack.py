import aws_cdk as cdk
from aws_cdk import Stack as CdkStack
from constructs import Construct

class Stack(CdkStack):
    def __init__(self, scope: Construct, id: str, tags: dict, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.add_tags(tags)

    def add_tags(self, tags: dict):
        for key, value in tags.items():
            cdk.Tags.of(self).add(key, value)