# pylint: disable=too-few-public-methods
"""
Configuration module for the Flask application.

This module contains the base configuration class and environment-specific
configuration classes for the Flask application.
"""

import os


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

    # App
    DEBUG = False
    LOG_LEVEL = "INFO"

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Cognito
    COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
    COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
    COGNITO_REGION = os.getenv("COGNITO_REGION")

    # Database
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
    DB_PORT = os.getenv("DB_PORT", "5432")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")


class DevelopmentConfig(Config):
    """Development environment configuration.

    Attributes:
        DEBUG (bool): Debug mode.
        LOG_LEVEL (str): Logging level.
    """

    # App
    DEBUG = True
    LOG_LEVEL = "DEBUG"
