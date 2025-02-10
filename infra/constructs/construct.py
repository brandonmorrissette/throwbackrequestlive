import logging

from aws_cdk import Construct as AwsCdKConstruct
from config import Config
from resources.resource import Resource


class Construct:
    def __init__(
        self,
        scope: AwsCdKConstruct,
        config: Config,
    ) -> None:
        # Resource.__init__(self, scope, config, id, suffix)
        # super().__init__(scope, id, env=config.cdk_environment)
        logging.info(f"Construct sanity check validation : {scope} {config}")
