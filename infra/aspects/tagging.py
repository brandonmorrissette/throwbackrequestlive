from aws_cdk import IAspect, Tags
from config import Config
from constructs import IConstruct


class ConfigTaggingAspect(IAspect):

    def __init__(self, env: Config):
        self.env = env

    def visit(self, node: IConstruct):
        if isinstance(node, IConstruct):
            Tags.of(node).add("project_name", self.env.project_name)
            Tags.of(node).add("environment_name", self.env.environment_name)
