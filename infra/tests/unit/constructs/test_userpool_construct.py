# pylint: disable=missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-variable
from unittest.mock import ANY, MagicMock, patch

import aws_cdk as cdk
import pytest

from infra.config import Config
from infra.constructs.construct import Construct
from infra.constructs.userpool import UserPoolConstruct, UserPoolConstructArgs
from infra.stacks.stack import Stack, StackArgs

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
    config: Config,
):
    user_pool_id = "user_pool_id"

    with patch("infra.constructs.userpool.boto3.client") as mock_boto3, patch(
        "infra.constructs.userpool.cognito"
    ) as mock_cognito:

        mock_boto3.return_value.list_user_pools.return_value = {
            "UserPools": [
                {
                    "Id": user_pool_id,
                    "Name": f"{config.project_name}-{config.environment_name}-user-pool",
                }
            ]
        }
        mock_cognito.UserPool.from_user_pool_id.return_value.user_pool_id = user_pool_id
        mock_cognito.UserPool.from_user_pool_id.return_value.add_client.return_value.user_pool_client_id = (  # pylint: disable=line-too-long
            "user_pool_client_id"
        )

        UserPoolConstruct(
            Stack(
                cdk.App(),
                StackArgs(
                    Config(
                        project_name="userpooltest",
                        environment_name="unit",
                        cdk_environment=cdk.Environment(
                            account="account", region="us-east-1"
                        ),
                    ),
                ),
            ),
            UserPoolConstructArgs(config=config),
        )

    mock_cognito.UserPool.from_user_pool_id.assert_called_once_with(
        ANY, ANY, user_pool_id=user_pool_id
    )


def test_app__client_creation(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
):
    construct, _, mock_cognito, _ = mock_userpool_construct

    mock_cognito.AuthFlow.assert_called_once_with(
        admin_user_password=True, user_password=True
    )
    mock_cognito.UserPool.return_value.add_client.assert_called_once_with(
        ANY,
        user_pool_client_name=ANY,
        auth_flows=mock_cognito.AuthFlow.return_value,
    )


def test_ssm_parameters_creation(
    mock_userpool_construct: tuple[UserPoolConstruct, MagicMock, MagicMock, MagicMock],
    config: Config,
):
    construct, _, _, mock_ssm = mock_userpool_construct

    mock_ssm.StringParameter.assert_any_call(
        construct,
        "UserPoolIdParameter",
        parameter_name=f"/{config.project_name}-{config.environment_name}/user-pool-id",
        string_value=ANY,
    )
    mock_ssm.StringParameter.assert_any_call(
        construct,
        "UserPoolClientIdParameter",
        parameter_name=f"/{config.project_name}-{config.environment_name}/user-pool-client-id",
        string_value=ANY,
    )
