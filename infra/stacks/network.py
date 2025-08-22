"""
This module defines the NetworkStack class, which sets up the network resources for the application.

It creates VPC and Certificate constructs using the provided configuration.
"""

from constructs import Construct

from infra.config import Config
from infra.constructs.cert import CertConstruct, CertConstructArgs
from infra.constructs.vpc import VpcConstruct, VpcConstructArgs
from infra.constructs.gateway import GatewayConstruct, GatewayConstructArgs
from infra.constructs.route_53 import Route53Construct, Route53ConstructArgs
from infra.stacks.stack import Stack, StackArgs


class NetworkStackArgs(StackArgs):  # pylint: disable=too-few-public-methods
    """
    Arguments for the NetworkStack.

    Attributes:
        config (Config): Configuration object.
        uid (str): The ID of the stack.
            Default is "network".
        prefix (str): The prefix for the stack name.
            Default is "{config.project_name}-{config.environment_name}-".
    """

    def __init__(
        self,
        config: Config,
        uid: str = "network",
        prefix: str = "",
    ) -> None:
        super().__init__(config, uid, prefix)


class NetworkStack(Stack):
    """
    This stack sets up the network resources for the application.

    It creates VPC and Certificate constructs using the provided configuration.
    """

    def __init__(
        self,
        scope: Construct,
        args: NetworkStackArgs,
    ) -> None:
        """
        Initialize the NetworkStack.

        Args:
            scope (Construct): The scope in which this stack is defined.
            args (NetworkStackArgs): The arguments for the stack.
        """
        super().__init__(scope, StackArgs(args.config, args.uid, args.prefix))

        self.vpc_construct = VpcConstruct(self, VpcConstructArgs(args.config))
        self.cert_construct = CertConstruct(self, CertConstructArgs(args.config))

        self.gateway_construct = GatewayConstruct(self, GatewayConstructArgs(
            args.config,
            self.vpc_construct.vpc,
            self.cert_construct.domain_name
        ))

        Route53Construct(
            self,
            Route53ConstructArgs(
                args.config,
                hosted_zone=self.cert_construct.hosted_zone,
                domain_name=self.cert_construct.domain_name
            ),
        )

