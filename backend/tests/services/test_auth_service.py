# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.config import Config
from backend.flask.exceptions.http import HTTPException
from backend.flask.services.auth import AuthService
from backend.tests.mock.errors import CLIENT_ERROR, ERROR_MESSAGE, STATUS_CODE


@pytest.fixture
def config():
    mock_config = MagicMock(spec=Config)
    mock_config.__init__()  # pylint: disable=unnecessary-dunder-call
    return mock_config


@pytest.fixture
def auth_service(config):
    with patch("boto3.client"):
        return AuthService(config)


def test_when_init_then_cognito_params_are_retrieved(config: Config):
    with patch("boto3.client") as mock_boto:
        service = AuthService(config)

    mock_boto.assert_any_call("cognito-idp", region_name=config.aws_default_region)
    mock_boto.assert_any_call("ssm", region_name=config.aws_default_region)

    mock_boto.return_value.get_parameter.assert_any_call(
        Name=f"/{config.project_name}/user-pool-client-id", WithDecryption=True
    )
    mock_boto.return_value.get_parameter.assert_any_call(
        Name=f"/{config.project_name}/user-pool-id", WithDecryption=True
    )

    service._client_id = mock_boto.return_value.get_parameter.return_value["Parameter"][
        "Value"
    ]
    service._user_pool_id = mock_boto.return_value.get_parameter.return_value[
        "Parameter"
    ]["Value"]


def test_given_valid_creds_when_authenticate_user_then_return_token(auth_service):
    with patch("backend.flask.services.auth.AuthService.generate_jwt") as generate_jwt:
        response = auth_service.authenticate_user("test_user", "test_password")
        assert response["token"] == generate_jwt.return_value


def test_given_boto_client_error_raised_when_authenticate_user_then_raise_http_exception(
    auth_service,
):
    auth_service._client.initiate_auth.side_effect = CLIENT_ERROR
    with pytest.raises(HTTPException) as e:
        auth_service.authenticate_user("test_user", "test_password")
        assert e.value.description == ERROR_MESSAGE
        assert e.value.code == STATUS_CODE


def test_given_new_password_required_response_when_authenticate_user_then_correct_response_returned(
    auth_service,
):
    with patch("backend.flask.services.auth.AuthService.generate_jwt") as generate_jwt:
        session = MagicMock()
        auth_service._client.initiate_auth.return_value = {
            "ChallengeName": "NEW_PASSWORD_REQUIRED",
            "Session": session,
        }
        response = auth_service.authenticate_user("test_user", "test_password")
        assert response["token"] == generate_jwt.return_value
        assert response["error"] == "NEW_PASSWORD_REQUIRED"
        assert response["session"] == session


def test_given_valid_creds_when_reset_password_then_return_token(auth_service):
    with patch("backend.flask.services.auth.AuthService.generate_jwt") as generate_jwt:
        response = auth_service.reset_password(
            "test_user", "test_password", "test_session"
        )
        assert response["token"] == generate_jwt.return_value


def test_given_boto_client_error_raised_when_reset_password_then_raise_http_exception(
    auth_service,
):
    auth_service._client.respond_to_auth_challenge.side_effect = CLIENT_ERROR
    try:
        auth_service.reset_password("test_user", "test_password", "test_session")
    except HTTPException as e:
        assert e.description == ERROR_MESSAGE
        assert e.code == STATUS_CODE


def test_given_username_when_get_groups_by_username_then_return_groups(auth_service):
    group_name = "test_group"
    groups = {"Groups": [{"GroupName": group_name}]}
    auth_service._client.admin_list_groups_for_user.return_value = groups
    assert auth_service.get_groups_by_username("test_user") == [group_name]


def test_given_boto_client_error_raised_when_get_groups_by_username_then_raise_http_exception(
    auth_service,
):
    auth_service._client.respond_to_auth_challenge.side_effect = CLIENT_ERROR
    try:
        auth_service.get_groups_by_username("test_user")
    except HTTPException as e:
        assert e.description == ERROR_MESSAGE
        assert e.code == STATUS_CODE


def test_given_username_and_groups_when_generate_jwt_then_return_token(auth_service):
    with patch("backend.flask.services.auth.jwt") as jwt, patch(
        "backend.flask.services.auth.datetime"
    ) as datetime, patch("backend.flask.services.auth.timedelta") as timedelta:
        username = "test_user"
        groups = ["test_group"]
        payload = {
            "sub": username,
            "username": username,
            "groups": groups,
            "iat": datetime.now.return_value,
            "exp": datetime.now.return_value + timedelta.return_value,
        }

        token = auth_service.generate_jwt("test_user", ["test_group"])
        jwt.encode.assert_called_once_with(
            payload,
            auth_service._jwt_secret_key,
            algorithm=auth_service._jwt_algorithm,
        )
        assert token == jwt.encode.return_value
