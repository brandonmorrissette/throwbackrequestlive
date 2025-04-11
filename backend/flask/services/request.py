"""
This module provides the RequestService class, which handles operations related to requests
in the application. It interacts with the database to retrieve and process request data.
"""

from datetime import datetime, timedelta
from io import BytesIO

from flask import current_app as app
from flask import make_response, redirect, request, url_for
from werkzeug.wrappers.response import Response

from backend.flask.services.data import DataService
from backend.flask.services.entrypoint import EntryPointService


class RequestService(EntryPointService, DataService):
    """
    Service class for handling operations related to requests.
    Inherits from DataService to provide database interaction capabilities.
    """

    def get_shows_by_entry_point_id(self, entry_point_id: str) -> list:
        """
        Get shows by entry point ID.

        Args:
            entry_point_id (str): The entry point ID.

        Returns:
            list: A list of shows.
        """
        return self.execute(
            """
            SELECT shows.*
            FROM shows
            JOIN entrypoints ON shows.entry_point_id = entrypoints.id
            WHERE entrypoints.id = :entry_point_id
            """,
            {"entry_point_id": entry_point_id},
        )

    def redirect(self, entry_point_id: str) -> Response:
        """
        Enforces uniqueness and then redirects to Requests page.
        :param entry_point_id: The entry_point_id for the submission.
        :return: Redirect response to the main page.
        """
        try:
            self._validate_entry_point_id(entry_point_id)
        except ValueError as e:
            app.logger.error(f"Entry Point Validation error: {e}")
            # Consider how I can send an error to the toasty notification.
            return make_response(redirect(url_for("renderblueprint.render_main")))

        uid = request.cookies.get("uid", "")
        if self._is_duplicate(uid, entry_point_id):
            return self._handle_duplicate_submission(uid)

        response = make_response(redirect(url_for("renderblueprint.render_request")))

        self.set_session_cookies(response)
        response.set_cookie(
            "showId",
            str(next(iter(self.get_shows_by_entry_point_id(entry_point_id))).get("id")),
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        response.set_cookie(
            "entryPointId",
            entry_point_id,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        app.logger.info("Redirecting to the request page.")
        return response

    def _validate_entry_point_id(self, entry_point_id: str) -> None:
        """
        Validate the entry point ID.
        :param entry_point_id: The entry point ID to validate.
        """
        error = ValueError("Invalid entryPointId")
        show = next(iter(self.get_shows_by_entry_point_id(entry_point_id)), {})

        if not show:
            app.logger.error("No show found for the given entry point ID.")
            raise error

        start_time = show.get("start_time", "")
        if (
            not start_time
            < datetime.now()
            < show.get("end_time", start_time + timedelta(hours=1))
        ):
            app.logger.error("The current time is outside the show time range.")
            raise error

    def _is_duplicate(self, uid: str, entry_point_id: str) -> bool:
        """
        Check if the submission is a duplicate.
        :param uid: The unique identifier for the submission.
        :param entry_point_id: The entry point ID for the submission.
        :return: True if the submission is a duplicate, otherwise False.
        """
        if uid:
            result = self.execute(
                """
                SELECT 1
                FROM submissions
                WHERE id = :uid AND entry_point_id = :entry_point_id
                LIMIT 1
                """,
                {"uid": uid, "entry_point_id": entry_point_id},
            )
            if result:
                app.logger.info("Duplicate submission detected.")
                return True

        return False

    def _handle_duplicate_submission(self, uid: str) -> Response:
        """
        Handle duplicate submission by redirecting to the main page."
        """

        redirect_args = self._get_duplicate_submission(uid)
        return redirect(
            url_for(
                "renderblueprint.render_main",
                songName=next(iter(redirect_args), {}).get(
                    "song_name", "UNABLE TO RETRIEVE SONG NAME"
                ),
            )
        )

    def _get_duplicate_submission(self, uid: str) -> list:
        """
        Get duplicate submission by uid.
        :param uid: The unique identifier for the submission.
        :return: JSON response with the duplicate submission details.
        """
        request_result = self.execute(
            """
            SELECT song_id
            FROM requests
            WHERE id = :uid
            """,
            {"uid": uid},
        )

        song_id = next(iter(request_result), {}).get("song_id")
        if not song_id:
            return []

        return self.execute(
            """
            SELECT *
            FROM songs
            WHERE id = :song_id
            """,
            {"song_id": song_id},
        )

    def get_request_count_by_show_id(self, show_id: str):
        """
        Retrieves the count of requests grouped by song name and band name for a specific show.

        Args:
            show_id (str): The unique identifier of the show.

        Returns:
            list: A list of tuples, where each tuple contains:
                - song_name (str): The name of the song.
                - band_name (str): The name of the band.
                - request_count (int): The count of requests for the song and band.
        """
        return self.execute(
            """
            SELECT song_id, COUNT(id) AS count
            FROM requests
            WHERE show_id = :show_id
            GROUP BY song_id
            ORDER BY count DESC
            """,
            {"show_id": show_id},
        )

    def get_demo_entry_point_id(self) -> str:
        """
        Retrieves the demo entry point ID from the database.
        Returns:
            str: The demo entry point ID.
        """
        return next(
            iter(
                self.execute(
                    """
            SELECT entry_point_id
            FROM shows
            WHERE name = 'DEMO'
            """,
                    None,
                )
            ),
            "",
        )

    def get_demo_qr(self) -> BytesIO:
        """
        Retrieves the QR code image for the demo entry point.
        Returns:
            BytesIO: A BytesIO object containing the QR code image data.
        """
        response = self.s3_client.get_object(
            Bucket=self.bucket_name, Key="entrypoints/DEMO/qr.png"
        )
        return BytesIO(response["Body"].read())
