"""
This module provides the RequestService class, which handles operations related to requests
in the application. It interacts with the database to retrieve and process request data.
"""

import uuid
from datetime import datetime

from flask import current_app as app
from flask import jsonify, make_response, redirect, request, url_for
from werkzeug.wrappers.response import Response

from backend.flask.services.data import DataService


class RequestService(DataService):
    """
    Service class for handling operations related to requests.
    Inherits from DataService to provide database interaction capabilities.
    """

    def redirect(self, show_hash: str) -> Response:
        """
        Enforces uniqueness and then redirects to Requests page.

        :return: Redirect response to the request page.
            Returns to main if show_hash is invalid.
        """
        request_id = request.cookies.get("totalRequestLiveRequestId", "")
        if self._is_duplicate(request_id, show_hash):
            app.logger.info("Duplicate request %s detected, redirecting to main page.", request_id)
            duplicate_request = self._get_duplicate_request(request_id)
            return redirect(
                url_for(
                    "renderblueprint.render_main",
                    songName=next(iter(duplicate_request), {}).get(
                        "display_name", "UNABLE TO RETRIEVE SONG NAME"
                    ),
                )
            )

        response = make_response(redirect(url_for("renderblueprint.render_request", show_hash=show_hash)))

        app.logger.info("Redirecting to the request page.")
        return response

    def write_request(self, song_request: dict) -> Response:
        """Writes the request.

        :param request: The data for the request.
        :return: The response to the write operation.
        """
        song_request["request_time"] = datetime.now().isoformat()
        song_request["request_id"] = uuid.uuid4().hex

        self.insert_rows("requests", [song_request])
        app.logger.info("Request %s written successfully.", song_request["request_id"])
        response = make_response(jsonify(song_request), 201)

        response.set_cookie(
            "totalRequestLiveRequestId",
            song_request["request_id"],
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        return response

    def get_requests_counts(self) -> list:
        """
        Get the requests for each song.
        :return: A list of dictionaries containing song IDs and their request counts.
        """
        result = self.execute(
            """
            SELECT song_id, COUNT(*) as request_count
            FROM requests
            GROUP BY song_id
            """
        )
        return result

    def _is_duplicate(self, request_id: str, show_hash: str) -> bool:
        """
        Check if the request is a duplicate.
        :param request_id: The unique identifier for the request.
        :param show_hash: The unique identifier for the show.
        :return: True if the request is a duplicate, otherwise False.
        """
        if request_id:
            result = self.execute(
                # pylint: disable=R0801
                """
                SELECT 1
                FROM requests
                WHERE request_id = :request_id AND show_hash = :show_hash
                LIMIT 1
                """,
                {"request_id": request_id, "show_hash": show_hash},
            )
            if result:
                app.logger.info("Duplicate request %s detected.", request_id)
                return True

        return False

    def _get_duplicate_request(self, request_id: str) -> list:
        """
        Get duplicate request by request_id.
        :param request_id: The unique identifier for the request.
        :return: JSON response with the duplicate request details.
        """
        request_result = self.execute(
            # pylint: disable=R0801
            """
            SELECT song_id
            FROM requests
            WHERE request_id = :request_id
            """,
            {"request_id": request_id},
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
