# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from typing import Generator, Tuple
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from backend.flask.services.entrypoint import EntryPointService

ENTRYPOINTID = "entry_point_id"


@pytest.fixture(autouse=True)
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture
def redis_client():
    return MagicMock()


@pytest.fixture
def mocks() -> Generator[Tuple[MagicMock,], None, None]:
    with patch("backend.flask.services.entrypoint.boto3") as mock_boto:
        yield mock_boto,


@pytest.fixture
def service(
    # pylint: disable=unused-argument
    redis_client: MagicMock,
    config: MagicMock,
    mocks: Generator[Tuple[MagicMock,], None, None],
    mock_sql_alchemy_libraries: Generator[None, None, None],
) -> EntryPointService:
    service = EntryPointService(redis_client, config)

    return service


def test_when_create_entrypoint_then_entry_point_created(service: EntryPointService):

    with patch(
        "backend.flask.services.entrypoint.uuid4", return_value=ENTRYPOINTID
    ) as mock_uuid, patch(
        "backend.flask.services.entrypoint.EntryPointService.insert_rows"
    ) as mock_insert_rows:
        entry_point_id = service.create_entrypoint()

    mock_insert_rows.assert_called_once_with(
        "entrypoints",
        [{"id": str(mock_uuid.return_value)}],
    )
    assert entry_point_id == ENTRYPOINTID


def test_given_url_when_create_qr_code_then_qr_code_created(
    service: EntryPointService,
) -> None:
    url = "https://example.com"

    with patch("backend.flask.services.entrypoint.qrcode.QRCode") as mock_qr_code:
        qr_code = service.create_qr_code(url)

    mock_qr_code.assert_called_once_with(
        version=1,
        error_correction=1,
        box_size=10,
        border=4,
    )
    mock_qr_code.return_value.add_data.assert_called_once_with(url)
    mock_qr_code.return_value.make.assert_called_once_with(fit=True)
    mock_qr_code.return_value.make_image.assert_called_once_with(
        fill_color="black", back_color="white"
    )
    assert qr_code == mock_qr_code.return_value.make_image.return_value


def test_given_path_when_create_qr_code_then_qr_code_stored(
    service: EntryPointService, mocks: Generator[Tuple[MagicMock,], None, None]
) -> None:
    (mock_boto,) = mocks
    path = MagicMock()

    with patch(
        "backend.flask.services.entrypoint.qrcode.QRCode"
    ) as mock_qr_code, patch("backend.flask.services.entrypoint.io") as mock_io:
        service.create_qr_code("example.com", path)

    mock_qr_code.return_value.make_image.return_value.save.assert_called_once_with(
        mock_io.BytesIO.return_value
    )
    path.rstrip.assert_called_once_with("/")
    mock_boto.client.return_value.put_object.assert_called_once_with(
        Bucket=service.bucket_name,
        Key=f"{path.rstrip.return_value}/qr.png",
        Body=mock_io.BytesIO.return_value,
        ContentType="image/png",
    )


def test_when_start_session_then_redirect(service: EntryPointService) -> None:
    with patch.object(service, "redirect") as mock_redirect:
        response = service.start_session(ENTRYPOINTID)

    mock_redirect.assert_called_once_with(ENTRYPOINTID)
    assert response == mock_redirect.return_value


def test_given_valid_access_token_cookie_when_validate_session_then_return_success(
    service: EntryPointService, app: Flask
) -> None:
    access_key = "access_key"

    with patch.object(
        service, "validate_access_key", return_value=True
    ) as mock_validate_access_key, app.test_request_context(
        headers={"Cookie": f"accessKey={access_key}"}
    ):
        response = service.validate_session()

    mock_validate_access_key.assert_called_once_with(access_key)
    assert response.status_code == 200
    assert response.json == {"success": True}


def test_given_invalid_access_token_cookie_when_validate_session_then_return_error(
    service: EntryPointService, app: Flask
) -> None:
    with patch.object(
        service, "validate_access_key", return_value=False
    ) as mock_validate_access_key, app.test_request_context(
        headers={"Cookie": f"accessKey=invalid_access_key"}
    ):
        response = service.validate_session()

    mock_validate_access_key.assert_called_once_with("invalid_access_key")
    assert response.status_code == 401
    assert response.json == {
        "success": False,
        "error": "Invalid access key",
        "code": 401,
    }


def test_given_entry_point_id_when_redirect_then_redirect_main(
    service: EntryPointService, app: Flask
) -> None:
    url = "renderblueprint.render_main"
    with patch.object(
        service, "set_session_cookies"
    ) as mock_set_session_cookies, patch(
        "backend.flask.services.entrypoint.url_for", return_value=url
    ) as mock_url_for:
        response = service.redirect(ENTRYPOINTID)

    mock_url_for.assert_called_once_with("renderblueprint.render_main")
    assert response.status_code == 302
    assert response.location == url
    mock_set_session_cookies.assert_called_once_with(response)


def test_given_response_when_set_session_cookies_then_cookies_set(
    service: EntryPointService,
) -> None:
    response = MagicMock()

    with patch.object(
        service, "generate_access_key"
    ) as mock_generate_access_key, patch.object(
        service, "generate_uid"
    ) as mock_generate_uid:
        updated_response = service.set_session_cookies(response)

    response.set_cookie.assert_any_call(
        "accessKey",
        mock_generate_access_key.return_value,
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    response.set_cookie.assert_any_call(
        "uid",
        mock_generate_uid.return_value,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    assert updated_response == response


def test_when_generate_uid_then_returns_uuid(service: EntryPointService) -> None:
    with patch("backend.flask.services.entrypoint.uuid4") as mock_uuid:
        uid = service.generate_uid()

    mock_uuid.assert_called_once()
    assert uid == str(mock_uuid.return_value)


def test_when_generate_access_key_then_access_key_is_generated(
    service: EntryPointService,
) -> None:
    with patch("backend.flask.services.entrypoint.secrets") as mock_secrets:
        access_key = service.generate_access_key()

    mock_secrets.token_urlsafe.assert_called_once_with(32)
    service._redis_client.set.assert_called_once_with(access_key, access_key)
    service._redis_client.expire.assert_called_once_with(access_key, 600)
    assert access_key == mock_secrets.token_urlsafe.return_value


def test_given_access_key_exists_when_validate_access_key_then_validate(
    service: EntryPointService,
) -> None:
    access_key = "access_key"
    service._redis_client.exists.return_value = 1
    assert service.validate_access_key(access_key)
    service._redis_client.exists.assert_called_once_with(access_key)


def test_given_access_key_does_not_exist_when_validate_access_key_then_invalidate(
    service: EntryPointService,
) -> None:
    service._redis_client.exists.return_value = 0
    assert not service.validate_access_key(MagicMock())
