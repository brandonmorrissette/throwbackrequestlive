# pylint: disable=too-few-public-methods
"""
Configuration module for the Flask application.

This module contains the base configuration class and environment-specific
configuration classes for the Flask application.
"""

import os


# pylint: disable=too-many-instance-attributes
class Config:
    """Base configuration class.

    Attributes:
        DEBUG (bool): Debug mode.
        LOG_LEVEL (str): Logging level.
        JWT_SECRET_KEY (str): JWT secret key.
        JWT_TOKEN_LOCATION (list): JWT token location.
        JWT_HEADER_NAME (str): JWT header name.
        JWT_HEADER_TYPE (str): JWT header type.
        COGNITO_APP_CLIENT_ID (str): Cognito app client ID.
        COGNITO_USER_POOL_ID (str): Cognito user pool ID.
        COGNITO_REGION (str): Cognito region.
        DB_USER (str): Database user.
        DB_PASSWORD (str): Database password.
        DB_HOST (str): Database host.
        DB_NAME (str): Database name.
        DB_ENGINE (str): Database engine.
        DB_PORT (int): Database port.
        REDIS_HOST (str): Redis host.
        REDIS_PORT (int): Redis port.
    """

    def __init__(self, environment=None, **overrides):

        if environment == "development":
            # Any string equates to True for bool
            overrides["debug"] = bool(os.getenv("DEBUG", "True"))

        # App
        self.debug = overrides.get("debug", bool(os.getenv("DEBUG")))
        self.log_level = overrides.get("log_level", os.getenv("LOG_LEVEL", "INFO"))

        # JWT
        self.jwt_secret_key = overrides.get(
            "jwt_secret_key", os.getenv("JWT_SECRET_KEY")
        )
        self.jwt_token_location = overrides.get(
            "jwt_token_location",
            os.getenv("JWT_TOKEN_LOCATION", "headers").split(","),
        )
        self.jwt_header_name = overrides.get(
            "jwt_header_name", os.getenv("JWT_HEADER_NAME", "Authorization")
        )
        self.jwt_header_type = overrides.get(
            "jwt_header_type", os.getenv("JWT_HEADER_TYPE", "Bearer")
        )

        # Cognito
        self.cognito_app_client_id = overrides.get(
            "cognito_app_client_id", os.getenv("COGNITO_APP_CLIENT_ID")
        )
        self.cognito_user_pool_id = overrides.get(
            "cognito_user_pool_id", os.getenv("COGNITO_USER_POOL_ID")
        )
        self.cognito_region = overrides.get(
            "cognito_region", os.getenv("COGNITO_REGION")
        )

        # Database
        self.db_user = overrides.get("db_user", os.getenv("DB_USER"))
        self.db_password = overrides.get("db_password", os.getenv("DB_PASSWORD"))
        self.db_host = overrides.get("db_host", os.getenv("DB_HOST"))
        self.db_name = overrides.get("db_name", os.getenv("DB_NAME"))
        self.db_engine = overrides.get(
            "db_engine", os.getenv("DB_ENGINE", "postgresql")
        )
        self.db_port = overrides.get("db_port", os.getenv("DB_PORT", "5432"))

        # Redis
        self.redis_host = overrides.get("redis_host", os.getenv("REDIS_HOST", "redis"))
        self.redis_port = overrides.get("redis_port", os.getenv("REDIS_PORT", "6379"))
