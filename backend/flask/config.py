# pylint: disable=too-few-public-methods
"""
Configuration module for the Flask application.

This module contains the base configuration class and environment-specific
configuration classes for the Flask application.
"""

import json
import os
from typing import Dict, List, Optional, Union

import boto3


# pylint: disable=too-many-instance-attributes
class Config:
    """Base configuration class.

    Attributes:
        environment (str): Environment name.
        project_name (str): Project name.
        debug (bool): Debug mode.
        log_level (str): Log level.
        jwt_secret_key (str): JWT secret key.
        jwt_token_location (list): JWT token location.
        jwt_header_name (str): JWT header name.
        jwt_header_type (str): JWT header type.
        aws_default_region (str): AWS region.
        db_user (str): Database user.
        db_password (str): Database password.
        db_host (str): Database host.
        db_name (str): Database name.
        db_engine (str): Database engine.
        db_port (str): Database port.
        redis_host (str): Redis host.
        redis_port (str): Redis port.
    """

    # pylint: disable=invalid-name
    def __init__(
        self,
        environment: Optional[str] = None,
        **overrides: Union[str, str | None],
    ) -> None:
        # AWS
        self.AWS_DEFAULT_REGION: Optional[str] = overrides.get(
            "aws_default_region", os.getenv("AWS_DEFAULT_REGION")
        )

        # Boto Clients
        secrets_client = boto3.client(
            "secretsmanager", region_name=self.AWS_DEFAULT_REGION
        )

        # App
        self.project_name: Optional[str] = overrides.get(
            "project_name", os.getenv("PROJECT_NAME")
        )
        self.debug: bool = bool(overrides.get("debug", os.getenv("DEBUG")))
        self.log_level: Optional[str] = overrides.get(
            "log_level", os.getenv("LOG_LEVEL", "DEBUG")
        )
        self.environment: str = environment or os.getenv("ENVIRONMENT", "local")

        # JWT
        self.JWT_SECRET_KEY: Optional[str] = overrides.get(
            "jwt_secret_key", os.getenv("JWT_SECRET_KEY")
        )
        self.JWT_TOKEN_LOCATION: Optional[List[str]] = (
            overrides.get("jwt_token_location", os.getenv("JWT_TOKEN_LOCATION"))
            or "headers"
        ).split(",")
        self.JWT_HEADER_NAME: Optional[str] = overrides.get(
            "jwt_header_name", os.getenv("JWT_HEADER_NAME", "Authorization")
        )
        self.JWT_HEADER_TYPE: Optional[str] = overrides.get(
            "jwt_header_type", os.getenv("JWT_HEADER_TYPE", "Bearer")
        )

        # Database
        self.db_secrets: Dict[str, str] = json.loads(
            secrets_client.get_secret_value(
                SecretId=f"{self.project_name}-{self.environment}-db-credentials"
            )["SecretString"]
        )
        self.db_user: Optional[str] = overrides.get(
            "db_user", os.getenv("DB_USER", self.db_secrets.get("username", ""))
        )
        self.db_password: Optional[str] = overrides.get(
            "db_password", os.getenv("DB_PASSWORD", self.db_secrets.get("password", ""))
        )
        self.db_host: Optional[str] = overrides.get(
            "db_host", os.getenv("DB_HOST", self.db_secrets.get("host", ""))
        )
        self.db_name: Optional[str] = overrides.get(
            "db_name", os.getenv("DB_NAME", self.db_secrets.get("dbname", ""))
        )
        self.db_engine: Optional[str] = overrides.get(
            "db_engine",
            os.getenv(
                "DB_ENGINE",
                self.db_secrets.get("engine", "postgres").replace(
                    "postgres", "postgresql+psycopg"
                ),
            ),
        )
        self.db_port: Optional[str] = overrides.get(
            "db_port", os.getenv("DB_PORT", self.db_secrets.get("port", "5432"))
        )

        # Redis
        self.redis_host: Optional[str] = overrides.get(
            "redis_host", os.getenv("REDIS_HOST", "redis")
        )
        self.redis_port: Optional[str] = overrides.get(
            "redis_port", os.getenv("REDIS_PORT", "6379")
        )
