# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
import string
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.flask.config import Config
from backend.flask.exceptions.http import HTTPException
from backend.flask.services.cognito import CognitoService, cognito_json_encoder
from backend.tests.mock.errors import CLIENT_ERROR, ERROR_MESSAGE, STATUS_CODE

GROUP_NAME = "test_group"
groups = {"Groups": [{"GroupName": GROUP_NAME}]}
USERNAME = "test_user"
EMAIL = "test_email"
USER = {"Username": USERNAME, "Email": EMAIL}
users = {"Users": [USER]}

REDIS_KEYS = ["key"]


@pytest.fixture
def config():
    mock_config = MagicMock(spec=Config)
    mock_config.__init__()  # pylint: disable=unnecessary-dunder-call
    return mock_config


@pytest.fixture
def cognito_service(config):
    with patch("boto3.client") as mock_boto_client, patch(
        "redis.StrictRedis"
    ) as mock_redis_client:
        mock_boto_client.return_value = MagicMock()
        mock_redis_client.return_value = MagicMock()
        mock_redis_client.return_value.keys.return_value = REDIS_KEYS
        return CognitoService(config)


def test_given_datetime_when_cognito_json_encoder_then_return_isoformat():
    test_datetime = MagicMock(spec=datetime)
    assert cognito_json_encoder(test_datetime) == test_datetime.isoformat.return_value


def test_given_unsupported_type_when_cognito_json_encoder_then_raise_type_error():
    with pytest.raises(TypeError) as e:
        obj = MagicMock()
        cognito_json_encoder(obj)
        assert str(e) == f"Type {type(obj)} not serializable"


def test_given_list_users_returns_users_when_read_rows_then_users_returned(
    cognito_service,
):
    cognito_service._cognito_client.list_users.return_value = users
    cognito_service._cognito_client.admin_list_groups_for_user.return_value = groups

    result = cognito_service.read_rows()

    expected = users["Users"]
    for user in expected:
        user["Groups"] = [GROUP_NAME]
    assert result == expected


def test_given_user_when_read_rows_then_set_user_in_redis(cognito_service):
    with patch.object(cognito_service, "_persist_user") as persist_user:
        cognito_service._cognito_client.list_users.return_value = users
        cognito_service._cognito_client.admin_list_groups_for_user.return_value = groups

        cognito_service.read_rows()

        persist_user.assert_called_once_with(USERNAME, USER)


def test_given_client_error_when_read_rows_then_raise_http_exception(cognito_service):
    cognito_service._cognito_client.list_users.side_effect = CLIENT_ERROR

    with pytest.raises(HTTPException) as e:
        cognito_service.read_rows()
        assert e.value.description == ERROR_MESSAGE
        assert e.value.code == STATUS_CODE


def test_given_rows_without_users_in_redis_when_write_rows_then_delete_users_called(
    cognito_service,
):
    with patch.object(cognito_service, "_delete_user") as delete_user:
        cognito_service.write_rows([])

        delete_user.assert_called_once_with(REDIS_KEYS[0])


def test_given_rows_with_users_not_in_redis_when_write_rows_then_add_rows_called(
    cognito_service,
):
    with patch.object(cognito_service, "_add_user") as add_user:
        cognito_service.write_rows([USER])

        add_user.assert_called_once_with(USER)


def test_given_rows_with_users_in_redis_when_write_rows_then_update_rows_called(
    cognito_service,
):
    with patch.object(cognito_service, "_update_user") as update_user:
        key = REDIS_KEYS[0]
        _user = {"Username": key}
        cognito_service.write_rows([_user])

        update_user.assert_called_once_with(key, _user)


def test_when_generate_temp_password_then_return_secrets(cognito_service):
    with patch("backend.flask.services.cognito.secrets") as mock_secrets:
        valid_characters = set(string.ascii_letters + string.digits + "!@#$%^&*()-_=+")
        mock_secrets.choice.side_effect = valid_characters
        temp_password = cognito_service._generate_temp_password()

        assert len(temp_password) == 12
        assert mock_secrets.choice.call_count == 12

        for call in mock_secrets.call_args_list:
            assert call[0][0] in valid_characters


def test_given_user_when_add_user_then_user_added(cognito_service):
    with patch.object(cognito_service, "_persist_user") as persist_user, patch.object(
        cognito_service, "_generate_temp_password"
    ) as generate_temp_password:
        cognito_service._add_user(USER)
        cognito_service._cognito_client.admin_create_user.assert_called_once_with(
            Username=EMAIL,
            UserPoolId=cognito_service._user_pool_id,
            UserAttributes=[{"Name": "email", "Value": EMAIL}],
            TemporaryPassword=generate_temp_password.return_value,
        )
        persist_user.assert_called_once_with(
            cognito_service._cognito_client.admin_create_user.return_value["User"][
                "Username"
            ],
            cognito_service._cognito_client.admin_create_user.return_value["User"],
        )


def test_given_user_when_update_user_then_user_updated(cognito_service):
    with patch.object(cognito_service, "_persist_user") as persist_user:
        cognito_service._update_user(USERNAME, USER)
        cognito_service._cognito_client.admin_update_user_attributes.assert_called_once_with(
            UserAttributes=[{"Name": "email", "Value": EMAIL}],
            UserPoolId=cognito_service._user_pool_id,
            Username=USERNAME,
        )
        persist_user.assert_called_once_with(USERNAME, USER)


def test_given_user_when_delete_user_then_user_deleted(cognito_service):
    with patch.object(cognito_service, "_remove_user") as remove_user:
        cognito_service._delete_user(USERNAME)
        cognito_service._cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=cognito_service._user_pool_id,
            Username=USERNAME,
        )
        remove_user.assert_called_once_with(USERNAME)


def test_given_username_and_user_when_persist_user_then_set_user_in_redis(
    cognito_service,
):
    with patch("backend.flask.services.cognito.json") as mock_json:
        cognito_service._persist_user(USERNAME, USER)

        mock_json.dumps.assert_called_once_with(USER, default=cognito_json_encoder)
        cognito_service._redis_client.set.assert_called_once_with(
            USERNAME, mock_json.dumps.return_value
        )


def test_given_username_when_remove_user_then_remove_user_from_redis(cognito_service):
    cognito_service._remove_user(USERNAME)
    cognito_service._redis_client.delete.assert_called_once_with(USERNAME)
