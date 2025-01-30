from aws_cdk import CfnResource, IAspect, Tags
from config import Config
from constructs import IConstruct


class ConfigTaggingAspect(IAspect):

    def __init__(self, env: Config):
        self.env = env

    def visit(self, node: IConstruct):
        if isinstance(node, CfnResource):
            for key, value in vars(self.env).items():
                if value:
                    Tags.of(node).add(key, str(value))
