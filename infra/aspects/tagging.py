from aws_cdk import CfnResource, IAspect, Tags
from config import Config
from constructs import IConstruct


class ConfigTaggingAspect(IAspect):

    def __init__(self, config: Config):
        self.config = config

    def visit(self, node: IConstruct):
        if isinstance(node, CfnResource):
            Tags.of(node).add("project_name", self.config.project_name)
            Tags.of(node).add("environment_name", self.config.environment_name)
            Tags.of(node).add("account", self.config.cdk_environment.account)
            Tags.of(node).add("region", self.config.cdk_environment.region)
