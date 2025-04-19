# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name
from typing import Any, Mapping

import pytest

from infra.config import Config
from infra.constructs.userpool import UserPoolConstruct, UserPoolConstructArgs
from infra.stacks.stack import Stack


@pytest.fixture(scope="module", autouse=True)
def construct(stack: Stack, config: Config) -> UserPoolConstruct:
    return UserPoolConstruct(
        stack,
        UserPoolConstructArgs(config=config),
    )


def test_user_pool(user_pools: Mapping[str, Any], config: Config) -> None:
    user_pool = next(iter(user_pools.values()))

    assert (
        user_pool["Properties"]["UserPoolName"]
        == f"{config.project_name}-{config.environment_name}-user-pool"
    )
    assert user_pool["Properties"]["Policies"]["PasswordPolicy"] == {
        "MinimumLength": 8,
        "RequireLowercase": False,
        "RequireUppercase": False,
        "RequireNumbers": False,
        "RequireSymbols": False,
    }


def test_user_pool_client(
    user_pool_clients: Mapping[str, Any], user_pools: Mapping[str, Any], config: Config
) -> None:
    user_pool_client = next(iter(user_pool_clients.values()))
    user_pool_id = next(iter(user_pools.keys()))

    assert (
        user_pool_client["Properties"]["ClientName"]
        == f"{config.project_name}-{config.environment_name}-user-pool-app-client"
    )
    assert user_pool_client["Properties"]["AllowedOAuthFlows"] == [
        "implicit",
        "code",
    ]
    assert user_pool_client["Properties"]["AllowedOAuthFlowsUserPoolClient"] is True
    assert user_pool_client["Properties"]["AllowedOAuthScopes"] == [
        "profile",
        "phone",
        "email",
        "openid",
        "aws.cognito.signin.user.admin",
    ]
    assert user_pool_client["Properties"]["ExplicitAuthFlows"] == [
        "ALLOW_USER_PASSWORD_AUTH",
        "ALLOW_ADMIN_USER_PASSWORD_AUTH",
        "ALLOW_REFRESH_TOKEN_AUTH",
    ]
    assert user_pool_client["Properties"]["SupportedIdentityProviders"] == [
        "COGNITO",
    ]
    assert user_pool_client["Properties"]["UserPoolId"]["Ref"] == user_pool_id


def test_ssm_parameters(ssm_parameters: Mapping[str, Any], config: Config) -> None:
    user_pool_id_param = next(
        param
        for param in ssm_parameters.values()
        if param["Properties"]["Name"]
        == f"/{config.project_name}-{config.environment_name}/user-pool-id"
    )
    user_pool_client_id_param = next(
        param
        for param in ssm_parameters.values()
        if param["Properties"]["Name"]
        == f"/{config.project_name}-{config.environment_name}/user-pool-client-id"
    )

    assert user_pool_id_param
    assert user_pool_client_id_param
