# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from datetime import datetime
from typing import Generator, Tuple
from unittest.mock import MagicMock, call, patch

import pytest
from flask import Flask
from werkzeug.http import parse_cookie

from backend.flask.services.request import RequestService

REQUEST_ID = "request_id"

SHOW_HASH = "show_hash"
SONG_ID = "song_id"

shows = [{"hash": SHOW_HASH}]
songs = [{"song_id": SONG_ID}]

MAIN_URL = "renderblueprint.render_main"
REQUEST_URL = "renderblueprint.render_request"


@pytest.fixture(autouse=True)
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture
def mocks() -> Generator[Tuple[MagicMock,], None, None]:
    with patch("backend.flask.services.SHOW_HASH.boto3") as mock_boto:
        yield (mock_boto,)


@pytest.fixture
def service(
    config: MagicMock,
) -> RequestService:
    with patch(
        "backend.flask.services.request.DataService.__init__",
        return_value=None,
    ):
        service = RequestService(config)

    return service


def test_given_duplicate_submission_when_redirect_then_redirect_to_main(
    service: RequestService,
    app: Flask,
):
    with patch.object(
        service, "_is_duplicate", return_value=True
    ) as mock_is_duplicate, patch(
        "backend.flask.services.request.url_for", return_value=MAIN_URL
    ), patch.object(
        service, "_get_duplicate_request", return_value=shows
    ) as mock_get_duplicate_request, app.test_request_context(
        headers={"Cookie": f"totalRequestLiveRequestId={REQUEST_ID}"}
    ):
        response = service.redirect(SHOW_HASH)

    mock_is_duplicate.assert_called_once_with(REQUEST_ID, SHOW_HASH)
    mock_get_duplicate_request.assert_called_once_with(REQUEST_ID)

    assert response.status_code == 302
    assert response.location == MAIN_URL


def test_given_unique_submission_when_redirect_then_redirect_to_request_page(
    service: RequestService,
    app: Flask,
):
    with patch.object(
        service, "_is_duplicate", return_value=False
    ) as mock_is_duplicate, patch(
        "backend.flask.services.request.url_for", return_value=REQUEST_URL
    ), app.test_request_context(
        headers={"Cookie": f"totalRequestLiveRequestId={REQUEST_ID}"}
    ):
        response = service.redirect(SHOW_HASH)

    mock_is_duplicate.assert_called_once_with(REQUEST_ID, SHOW_HASH)

    assert response.status_code == 302
    assert response.location == REQUEST_URL


def test_given_song_request_when_write_request_then_writes_request(
    service: RequestService,
):
    request_id = "request_id"
    request_time = datetime(2024, 1, 1, 12, 0, 0)
    song_request = {"song_name": "Test Song"}

    with patch.object(service, "insert_rows") as mock_insert_rows, patch(
        "uuid.uuid4", return_value=MagicMock(hex=request_id)
    ), patch("backend.flask.services.request.datetime") as mock_datetime:
        mock_datetime.now.return_value = request_time

        response = service.write_request(song_request)

    expected_request = {
        "song_name": "Test Song",
        "request_time": request_time.isoformat(),
        "request_id": request_id,
    }

    mock_insert_rows.assert_called_once_with("requests", [expected_request])

    assert response.status_code == 201
    assert response.get_json() == expected_request


def test_given_song_request_when_write_request_then_sets_cookie(
    service: RequestService,
):
    request_id = "request_id"
    song_request = {"song_name": "Test Song"}

    with patch.object(service, "insert_rows"), patch(
        "uuid.uuid4", return_value=MagicMock(hex=request_id)
    ):

        response = service.write_request(song_request)

    cookies = parse_cookie(response.headers["Set-Cookie"])
    assert cookies.get("totalRequestLiveRequestId") == request_id


def test_when_get_requests_counts_then_returns_counts(
    service: RequestService,
):
    with patch.object(service, "execute") as mock_execute:
        result = service.get_requests_counts()

    mock_execute.assert_called_once_with(
        """
            SELECT song_id, COUNT(*) as request_count
            FROM requests
            GROUP BY song_id
            """
    )
    assert result == mock_execute.return_value


def test_given_no_uid_when_is_duplicate_then_returns_false(
    service: RequestService,
):
    result = service._is_duplicate("", SHOW_HASH)
    assert not result


def test_given_uid_and_execute_returns_none_when_is_duplicate_then_returns_false(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=None) as mock_execute:
        result = service._is_duplicate(REQUEST_ID, SHOW_HASH)

    mock_execute.assert_called_once_with(
        """
                SELECT 1
                FROM requests
                WHERE request_id = :request_id AND show_hash = :show_hash
                LIMIT 1
                """,
        {"request_id": REQUEST_ID, "show_hash": SHOW_HASH},
    )
    assert not result


def test_given_uid_and_execute_returns_value_when_is_duplicate_then_returns_true(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=[{"1": 1}]) as mock_execute:
        result = service._is_duplicate(REQUEST_ID, SHOW_HASH)

    mock_execute.assert_called_once_with(
        """
                SELECT 1
                FROM requests
                WHERE request_id = :request_id AND show_hash = :show_hash
                LIMIT 1
                """,
        {"request_id": REQUEST_ID, "show_hash": SHOW_HASH},
    )
    assert result


def test_given_request_id_when_get_duplicate_request_then_returns_request(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=songs) as mock_execute:
        mock_execute.side_effect = [
            [songs[0]],
            songs,
        ]
        result = service._get_duplicate_request(REQUEST_ID)

    song_id_call = call(
        """
            SELECT song_id
            FROM requests
            WHERE request_id = :request_id
            """,
        {"request_id": REQUEST_ID},
    )
    song_call = call(
        """
            SELECT *
            FROM songs
            WHERE id = :song_id
            """,
        {"song_id": SONG_ID},
    )

    mock_execute.assert_has_calls(
        [
            song_id_call,
            song_call,
        ]
    )
    assert result == songs


def test_given_request_id_when_get_duplicate_request_and_no_song_id_then_returns_empty_list(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=[]):
        result = service._get_duplicate_request(REQUEST_ID)

    assert result == []
