# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import ANY, MagicMock, patch

import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.userpool import UserPoolConstruct, UserPoolConstructArgs
from infra.stacks.stack import Stack

USER_POOL_ID = "mock_user_pool_id"


@pytest.fixture(scope="module")
def mock_userpool_construct(config: Config, stack: Stack):
    with patch("infra.constructs.userpool.boto3.client") as mock_boto3, patch(
        "infra.constructs.userpool.cognito"
    ) as mock_cognito, patch("infra.constructs.userpool.ssm") as mock_ssm:
        mock_cognito.UserPool.return_value.user_pool_id = USER_POOL_ID
        yield UserPoolConstruct(
            stack, UserPoolConstructArgs(config)
        ), mock_boto3, mock_cognito, mock_ssm


def test_construct_inheritance():
    assert issubclass(UserPoolConstruct, Construct)


def test_default_id(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
    config: Config,
):
    construct, _, _, _ = mock_userpool_construct
    assert (
        construct.node.id
        == f"{config.project_name}-{config.environment_name}-user-pool"
    )


def test_user_pool_creation(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
):
    construct, mock_boto3, mock_cognito, _ = mock_userpool_construct

    mock_boto3.return_value.list_user_pools.assert_called_once_with(MaxResults=60)

    mock_cognito.UserPool.assert_called_once_with(
        construct,
        ANY,
        user_pool_name=ANY,
        self_sign_up_enabled=False,
        sign_in_aliases=mock_cognito.SignInAliases.return_value,
        password_policy=mock_cognito.PasswordPolicy.return_value,
        account_recovery=mock_cognito.AccountRecovery.EMAIL_ONLY,
    )


def test_given_user_pool_exists_when_user_pool_construct_created_then_user_pool_is_retrieved(
    stack: Stack,
    config: Config,
):

    user_pool_name = f"{config.project_name}-user-pool"

    def side_effect(key):
        if key == "Name":
            return user_pool_name
        if key == "Id":
            return USER_POOL_ID
        return key

    userpool = MagicMock()
    userpool.__getitem__.side_effect = side_effect

    with patch("infra.constructs.userpool.boto3.client") as mock_boto3, patch(
        "infra.constructs.userpool.cognito"
    ) as mock_cognito:
        mock_boto3.return_value.list_user_pools.return_value = {
            "UserPools": [{"Id": USER_POOL_ID, "Name": user_pool_name}]
        }

        mock_cognito.UserPoolClient.from_user_pool_client_id.return_value.user_pool_client_id = (
            "mock_user_pool_client_id"
        )
        mock_cognito.UserPool.from_user_pool_id.return_value.user_pool_id = USER_POOL_ID
        mock_cognito.UserPool.return_value.user_pool_id = USER_POOL_ID

        mock_boto3.return_value.list_user_pools.return_value = {"UserPools": [userpool]}
        UserPoolConstruct(stack, UserPoolConstructArgs(config=config))

    mock_cognito.UserPool.from_user_pool_id.assert_called_once_with(
        ANY, ANY, user_pool_id=userpool["Id"]
    )


def test_user_pool_client_creation(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
):
    construct, mock_boto3, mock_cognito, _ = mock_userpool_construct

    mock_boto3.return_value.list_user_pool_clients.assert_called_once_with(
        UserPoolId=ANY, MaxResults=60
    )
    mock_cognito.CfnUserPoolClient.assert_called_once_with(
        construct,
        ANY,
        user_pool_id=ANY,
        client_name=ANY,
        explicit_auth_flows=[
            "ALLOW_ADMIN_USER_PASSWORD_AUTH",
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
        ],
    )
    mock_cognito.UserPoolClient.from_user_pool_client_id.assert_called_once_with(
        construct, ANY, user_pool_client_id=ANY
    )


def test_ssm_parameters_creation(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
    config: Config,
):
    construct, _, _, mock_ssm = mock_userpool_construct

    mock_ssm.StringParameter.assert_any_call(
        construct,
        "UserPoolIdParameter",
        parameter_name=f"/{config.project_name}/user-pool-id",
        string_value=ANY,
    )
    mock_ssm.StringParameter.assert_any_call(
        construct,
        "UserPoolClientIdParameter",
        parameter_name=f"/{config.project_name}/user-pool-client-id",
        string_value=ANY,
    )
