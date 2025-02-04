import jsii
from aws_cdk import IAspect, Tags
from config import Config
from constructs import IConstruct


@jsii.implements(IAspect)
class ConfigTaggingAspect:

    def __init__(self, config: Config):
        self.config = config

    def visit(self, node: IConstruct):
        if isinstance(node, IConstruct):
            Tags.of(node).add("project_name", self.config.project_name)
            Tags.of(node).add("environment_name", self.config.environment_name)
