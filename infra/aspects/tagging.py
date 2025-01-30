from aws_cdk import IAspect, Tags
from constructs import IConstruct

from infra.config import Config


class ConfigTaggingAspect(IAspect):

    def __init__(self, env: Config):
        self.env = env

    def visit(self, node: IConstruct):
        if isinstance(node, IConstruct):
            for key, value in vars(self.env).items():
                if value:
                    Tags.of(node).add(key, str(value))
