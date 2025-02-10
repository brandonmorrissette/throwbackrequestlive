import logging

from aws_cdk import Construct as AwsCdKConstruct
from config import Config
from resources.resource import Resource


class Construct(AwsCdKConstruct):
    def __init__(
        self,
        scope: AwsCdKConstruct,
        config: Config,
        id: str | None = None,
        suffix: str | None = None,
    ) -> None:
        # Resource.__init__(self, scope, config, id, suffix)
        # super().__init__(scope, id, env=config.cdk_environment)
        logging.info("Construct sanity check validation")
