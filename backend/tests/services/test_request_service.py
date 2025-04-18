# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from typing import Generator, Tuple
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import pytest
from flask import Flask

from backend.flask.services.request import RequestService


ENTRYPOINT = "entrypoint"
UID = "uid"

SHOW_ID = "show_id"
SONG_ID = "song_id"

shows = [{"id": SHOW_ID}]
songs = [{"id": SONG_ID}]

MAIN_URL = "renderblueprint.render_main"
REQUEST_URL = "renderblueprint.render_request"


@pytest.fixture(autouse=True)
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture
def mocks() -> Generator[Tuple[MagicMock,], None, None]:
    with patch("backend.flask.services.entrypoint.boto3") as mock_boto:
        yield (mock_boto,)


@pytest.fixture
def service(
    # pylint: disable=unused-argument
    redis_client: MagicMock,
    config: MagicMock,
    mocks: Generator[Tuple[MagicMock], None, None],
    mock_sql_alchemy_libraries: Generator[None, None, None],
) -> RequestService:
    service = RequestService(redis_client, config)
    return service


def test_given_entry_point_id_when_get_shows_by_entry_point_id_then_shows_retrieved(
    service: RequestService,
):

    with patch(
        "backend.flask.services.request.RequestService.execute",
        return_value=shows,
    ) as mock_execute:
        response = service.get_shows_by_entry_point_id(ENTRYPOINT)

    mock_execute.assert_called_once_with(
        """
            SELECT shows.*
            FROM shows
            JOIN entrypoints ON shows.entry_point_id = entrypoints.id
            WHERE entrypoints.id = :entry_point_id
            """,
        {"entry_point_id": ENTRYPOINT},
    )

    assert response == shows


def test_given_invalid_entry_point_id_when_redirect_then_redirect_to_main(
    service: RequestService
):
    with patch.object(
        service,
        "_validate_entry_point_id",
        side_effect=ValueError("Invalid entryPointId"),
    ) as mock_validate_entry_point_id, patch(
        "backend.flask.services.request.url_for", return_value=MAIN_URL
    ):
        response = service.redirect("invalid_entry_point_id")

    assert response.status_code == 302
    assert response.location == MAIN_URL
    mock_validate_entry_point_id.assert_called_once_with("invalid_entry_point_id")


def test_given_duplicate_submission_when_redirect_then_handle_duplicate(
    service: RequestService,
    app: Flask,
):
    with patch.object(
        service, "_is_duplicate", return_value=True
    ) as mock_is_duplicate, patch.object(
        service,
        "_validate_entry_point_id",
    ), patch(
        "backend.flask.services.request.url_for", return_value=MAIN_URL
    ), patch.object(
        service, "_handle_duplicate_submission"
    ) as mock_handle_duplicate_submission, app.test_request_context(
        headers={"Cookie": f"uid={UID}"}
    ):
        response = service.redirect(ENTRYPOINT)

    mock_is_duplicate.assert_called_once_with(UID, ENTRYPOINT)
    mock_handle_duplicate_submission.assert_called_once_with(UID)
    assert response == mock_handle_duplicate_submission.return_value


def test_given_entry_point_id_when_redirect_then_redirect_to_request_page(
    service: RequestService, app: Flask
):
    with patch.object(service, "_validate_entry_point_id"), patch.object(
        service, "_is_duplicate", return_value=False
    ), patch(
        "backend.flask.services.request.url_for", return_value=REQUEST_URL
    ), patch.object(
        service, "get_shows_by_entry_point_id", return_value=shows
    ), patch.object(
        service, "set_session_cookies"
    ) as mock_set_session_cookies, app.test_request_context(
        headers={"Cookie": f"uid={UID}"}
    ):
        response = service.redirect(ENTRYPOINT)

    assert response.status_code == 302
    assert response.location == REQUEST_URL

    # Cookies
    mock_set_session_cookies.assert_called_once_with(response)
    assert (
        f"showId={SHOW_ID}; Secure; HttpOnly; Path=/; SameSite=Lax"
        in response.headers.getlist("Set-Cookie")
    )
    assert (
        f"entryPointId={ENTRYPOINT}; Secure; HttpOnly; Path=/; SameSite=Lax"
        in response.headers.getlist("Set-Cookie")
    )


def test_given_entry_point_with_no_shows_when_validate_entry_point_id_then_raises_error(
    service: RequestService,
):
    with patch.object(
        service, "get_shows_by_entry_point_id", return_value=[]
    ) as mock_get_shows_by_entry_point_id:
        with pytest.raises(ValueError, match="Invalid entryPointId"):
            service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_show_start_time_after_now_when_validate_entry_point_id_then_raises_error(
    service: RequestService,
):
    with patch.object(
        service,
        "get_shows_by_entry_point_id",
        return_value=[
            {
                "start_time": datetime.now() + timedelta(hours=2),
            }
        ],
    ) as mock_get_shows_by_entry_point_id:
        with pytest.raises(ValueError, match="Invalid entryPointId"):
            service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_show_start_time_within_last_hour_when_validate_entry_point_id_then_continue(
    service: RequestService,
):
    with patch.object(
        service,
        "get_shows_by_entry_point_id",
        return_value=[
            {
                "start_time": datetime.now() - timedelta(minutes=30),
            }
        ],
    ) as mock_get_shows_by_entry_point_id:
        service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_show_end_time_before_now_when_validate_entry_point_id_then_raises_error(
    service: RequestService,
):
    with patch.object(
        service,
        "get_shows_by_entry_point_id",
        return_value=[
            {
                "start_time": datetime.now() - timedelta(hours=2),
                "end_time": datetime.now(),
            }
        ],
    ) as mock_get_shows_by_entry_point_id:
        with pytest.raises(ValueError, match="Invalid entryPointId"):
            service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_show_with_no_end_time_and_show_started_within_last_hour_when_validate_entry_point_id_then_continue( # pylint: disable=line-too-long
    service: RequestService,
):
    with patch.object(
        service,
        "get_shows_by_entry_point_id",
        return_value=[
            {
                "start_time": datetime.now() - timedelta(minutes=30),
            }
        ],
    ) as mock_get_shows_by_entry_point_id:
        service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_show_with_no_end_time_and_show_not_started_within_last_hour_when_validate_entry_point_id_then_raises_error( # pylint: disable=line-too-long
    service: RequestService,
):
    with patch.object(
        service,
        "get_shows_by_entry_point_id",
        return_value=[
            {
                "start_time": datetime.now() - timedelta(hours=2),
            }
        ],
    ) as mock_get_shows_by_entry_point_id:
        with pytest.raises(ValueError, match="Invalid entryPointId"):
            service._validate_entry_point_id(ENTRYPOINT)

    mock_get_shows_by_entry_point_id.assert_called_once_with(ENTRYPOINT)


def test_given_no_uid_when_is_duplicate_then_returns_false(
    service: RequestService,
):
    result = service._is_duplicate(None, ENTRYPOINT)
    assert not result


def test_given_uid_and_unique_entry_point_id_when_is_duplicate_then_returns_false(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=None) as mock_execute:
        result = service._is_duplicate(UID, ENTRYPOINT)

    mock_execute.assert_called_once_with(
        """
                SELECT 1
                FROM submissions
                WHERE id = :uid AND entry_point_id = :entry_point_id
                LIMIT 1
                """,
        {"uid": UID, "entry_point_id": ENTRYPOINT},
    )
    assert not result


def test_given_uid_and_duplicate_entry_point_id_when_is_duplicate_then_returns_true(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=[{"1": 1}]) as mock_execute:
        result = service._is_duplicate(UID, ENTRYPOINT)

    mock_execute.assert_called_once_with(
        # pylint: disable=R0801
        """
                SELECT 1
                FROM submissions
                WHERE id = :uid AND entry_point_id = :entry_point_id
                LIMIT 1
                """,
        {"uid": UID, "entry_point_id": ENTRYPOINT},
    )
    assert result


def test_given_uid_when_handle_duplicate_submission_then_redirect_to_main(
    service: RequestService,
):
    song_name = "Duplicate Song"
    duplicate_song = {"song_name": song_name}
    with patch(
        "backend.flask.services.request.url_for", return_value=MAIN_URL
    ) as mock_url_for, patch.object(
        service, "_get_duplicate_submission", return_value=[duplicate_song]
    ):
        response = service._handle_duplicate_submission(UID)

    assert response.status_code == 302
    assert response.location == MAIN_URL
    mock_url_for.assert_called_once_with(
        "renderblueprint.render_main", songName=song_name
    )


def test_given_uid_when_get_duplicate_submission_then_return_song(
    service: RequestService,
):

    with patch.object(
        service, "execute", side_effect=[[{"song_id": SONG_ID}], songs]
    ) as mock_execute:
        result = service._get_duplicate_submission(UID)

    mock_execute.assert_any_call(
        # pylint: disable=R0801
        """
            SELECT song_id
            FROM requests
            WHERE id = :uid
            """,
        {"uid": UID},
    )
    mock_execute.assert_called_with(
        """
            SELECT *
            FROM songs
            WHERE id = :song_id
            """,
        {"song_id": SONG_ID},
    )
    assert result == songs


def test_given_no_song_id_when_get_duplicate_submission_then_return_empty_list(
    service: RequestService,
):
    with patch.object(service, "execute", return_value=[]) as mock_execute:
        result = service._get_duplicate_submission(UID)

    mock_execute.assert_called_once_with(
        """
            SELECT song_id
            FROM requests
            WHERE id = :uid
            """,
        {"uid": UID},
    )
    assert result == []


def test_given_show_id_when_get_request_count_by_show_id_then_return_request_count(
    service: RequestService,
):

    with patch.object(service, "execute") as mock_execute:
        result = service.get_request_count_by_show_id(SHOW_ID)

    mock_execute.assert_called_once_with(
        # pylint: disable=R0801
        """
            SELECT song_id, COUNT(id) AS count
            FROM requests
            WHERE show_id = :show_id
            GROUP BY song_id
            ORDER BY count DESC
            """,
        {"show_id": SHOW_ID},
    )
    assert result == mock_execute.return_value


def test_get_demo_entry_point_id(service: RequestService):
    with patch.object(
        service, "execute", return_value=[{"entry_point_id": ENTRYPOINT}]
    ) as mock_execute:
        result = service.get_demo_entry_point_id()

    mock_execute.assert_called_once_with(
        """
                        SELECT entry_point_id
                        FROM shows
                        WHERE name = 'DEMO'
                        """,
        None,
    )
    assert result == ENTRYPOINT


def test_get_demo_qr(
    service: RequestService, mocks: Generator[Tuple[MagicMock,], None, None]
):
    (mock_boto,) = mocks
    with patch("backend.flask.services.request.BytesIO") as mock_bytes_io:
        response = service.get_demo_qr()

    mock_boto.client.return_value.get_object.assert_called_once_with(
        Bucket=service.bucket_name,
        Key="entrypoints/DEMO/qr.png",
    )
    mock_bytes_io.assert_called_once_with(
        mock_boto.client.return_value.get_object.return_value["Body"].read()
    )
    assert response == mock_bytes_io.return_value
