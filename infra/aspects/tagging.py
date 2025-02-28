import jsii
from aws_cdk import IAspect, Tags
from config import Config
from constructs import IConstruct


@jsii.implements(IAspect)
class TaggingAspect:
    """
    An aspect that adds default tags to all nodes in the AWS CDK construct tree.
    """

    def __init__(self, config: Config):
        """
        Initialize the TaggingAspect.

        :param config: Configuration object
        """
        self.config = config

    def visit(self, node: IConstruct):
        """
        Visit each node in the construct tree and add tags.

        :param node: The construct node to tag.
        """
        if hasattr(node, "node"):
            if self.config.project_name:
                Tags.of(node).add("project_name", self.config.project_name)
            if self.config.environment_name:
                Tags.of(node).add("environment_name", self.config.environment_name)
