"""
This module contains the Config class, which holds configuration details for the AWS CDK application.

Classes:
    Config: A class that holds configuration details.

Usage example:
    config = Config(project_name, environment_name, cdk_environment)
"""

import aws_cdk as cdk


class Config:
    """
    A class that holds configuration details for the AWS CDK application.

    Attributes:
        project_name: The name of the project.
        environment_name: The name of the environment.
        cdk_environment: The AWS CDK environment configuration.

    Methods:
        __init__: Initializes the Config with the given parameters.
        __str__: Returns a string representation of the Config object.
    """

    def __init__(
        self,
        project_name: str | None,
        environment_name: str | None,
        cdk_environment: cdk.Environment | None,
    ) -> None:
        """
        Initializes the Config with the given parameters.

        Args:
            project_name (str, optional): The name of the project. Defaults to None.
            environment_name (str, optional): The name of the environment. Defaults to None.
            cdk_environment (cdk.Environment, optional): The AWS CDK environment configuration. Defaults to None.
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.cdk_environment = cdk_environment

    def __str__(self) -> str:
        """
        Returns a string representation of the Config object.

        Returns:
            str: A string representation of the Config object.
        """
        return f"Config(project_name={self.project_name}, environment_name={self.environment_name}, cdk_environment={self.cdk_environment})"
