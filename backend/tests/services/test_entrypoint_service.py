# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from typing import Generator, Tuple
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from backend.flask.services.entrypoint import EntryPointService

ENTRYPOINT = "entrypoint"


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
        yield mock_boto


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
        "backend.flask.services.entrypoint.uuid4", return_value=ENTRYPOINT
    ) as mock_uuid, patch(
        "backend.flask.services.entrypoint.EntryPointService.insert_rows"
    ) as mock_insert_rows:
        entry_point_id = service.create_entrypoint()

    mock_insert_rows.assert_called_once_with(
        "entrypoints",
        [{"id": str(mock_uuid.return_value)}],
    )
    assert entry_point_id == ENTRYPOINT


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
