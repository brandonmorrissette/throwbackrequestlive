# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
import string
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

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
def cognito_service(config: MagicMock) -> CognitoService:
    with patch("boto3.client"):
        return CognitoService(config)


def test_given_datetime_when_cognito_json_encoder_then_return_isoformat() -> None:
    test_datetime = MagicMock(spec=datetime)
    assert cognito_json_encoder(test_datetime) == test_datetime.isoformat.return_value


def test_given_unsupported_type_when_cognito_json_encoder_then_raise_type_error() -> (
    None
):
    with pytest.raises(TypeError) as e:
        obj = MagicMock()
        cognito_json_encoder(obj)
        assert str(e) == f"Type {type(obj)} not serializable"


def test_given_list_users_returns_users_when_read_rows_then_users_returned(
    cognito_service: CognitoService,
) -> None:
    cognito_service._cognito_client.list_users.return_value = users
    cognito_service._cognito_client.admin_list_groups_for_user.return_value = groups

    result = cognito_service.read_rows()

    expected = users["Users"]
    for user in expected:
        user["Groups"] = GROUP_NAME
    assert result == expected


def test_given_client_error_when_read_rows_then_raise_http_exception(
    cognito_service: CognitoService,
) -> None:
    cognito_service._cognito_client.list_users.side_effect = CLIENT_ERROR

    with pytest.raises(HTTPException) as e:
        cognito_service.read_rows()
        assert e.value.description == ERROR_MESSAGE
        assert e.value.code == STATUS_CODE


def test_when_generate_temp_password_then_return_secrets(
    cognito_service: CognitoService,
) -> None:
    with patch("backend.flask.services.cognito.secrets") as mock_secrets:
        valid_characters = set(string.ascii_letters + string.digits + "!@#$%^&*()-_=+")
        mock_secrets.choice.side_effect = valid_characters
        temp_password = cognito_service._generate_temp_password()

        assert len(temp_password) == 12
        assert mock_secrets.choice.call_count == 12

        for call in mock_secrets.call_args_list:
            assert call[0][0] in valid_characters
