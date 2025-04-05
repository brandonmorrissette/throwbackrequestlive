"""
This module provides functionality for managing short term sessions
and redirects in a Flask application.
It includes a Factory class that handles session
creation, validation, redirection, and session-related operations.
"""

from datetime import datetime, timedelta
from typing import Any, Tuple

from flask import current_app as app
from flask import jsonify, make_response, redirect, request, url_for
from werkzeug.wrappers.response import Response

from backend.flask.services.auth import AuthService, RequestAuthService


class SessionFactory:
    """
    Factory class for managing sessions and redirects.
    """

    def __init__(self, service: AuthService) -> None:
        self.service = service

    def start(self, entry_point_id: str) -> Response:
        """
        Start a session for the provided entry point ID.
        :param entry_point_id: The entry point ID to start a session for.
        """
        app.logger.info(f"Starting session for Entry point ID: {entry_point_id}")
        return self._get_redirect(entry_point_id)

    def validate_session(self) -> Tuple[Any, int]:
        """
        Validate the session for the provided entry point ID.
        :return: True if the session is valid, otherwise False.
        """
        access_key = request.cookies.get("accessKey", "")
        if self.service.validate_access_key(access_key):
            app.logger.debug(f"Access key is valid. {access_key}")
            return jsonify({"success": True}), 200

        app.logger.debug(f"Access key is invalid. {access_key}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid access key",
                    "code": 401,
                }
            ),
            401,
        )

    def _get_redirect(self, entry_point_id: str) -> Response:
        """
        Redirect to the main page with the given UID.
        :param entry_point_id: The entry_point_id for the submission.
        :return: Redirect response to the main page.
        """
        app.logger.info(f"Redirecting Entry point ID: {entry_point_id}")
        response = make_response(redirect(url_for("renderblueprint.render_main")))

        self._set_session_cookies(response)

        return response

    def _set_session_cookies(self, response: Response) -> Response:
        """
        Set cookies for the session.
        :param response: The response object to set cookies on.
        :return: The response object with default cookies set.
        """
        self._set_cookie(response, "accessKey", self.service.generate_access_key())
        self._set_cookie(response, "uid", self.service.generate_uid())

        return response

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def _set_cookie(
        self,
        response: Response,
        cookie_name: str,
        cookie_value: str,
        httponly: bool = True,
        secure: bool = True,
        samesite: str = "Lax",
    ) -> Response:
        """
        Set a specific cookie for the session.
        :param response: The response object to set the cookie on.
        :param cookie_name: The name of the cookie to set.
        :param cookie_value: The value of the cookie to set.
        :param httponly: Whether the cookie is HTTP only.
        :param secure: Whether the cookie is secure.
        :param samesite: The SameSite attribute for the cookie.
        :return: The response object with the specified cookie set.
        """
        response.set_cookie(
            cookie_name,
            cookie_value,
            httponly=httponly,
            secure=secure,
            samesite=samesite,
        )
        return response


class RequestSessionFactory(SessionFactory):
    """
    Factory class for managing request sessions and redirects.
    """

    service: RequestAuthService

    def _get_redirect(self, entry_point_id: str) -> Response:
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
        self._set_session_cookies(response)
        self._set_cookie(
            response,
            "showId",
            str(
                next(
                    iter(self.service.get_shows_by_entry_point_id(entry_point_id))
                ).get("id")
            ),
        )
        self._set_cookie(
            response,
            "entryPointId",
            entry_point_id,
        )

        app.logger.info("Redirecting to the request page.")
        return response

    def _validate_entry_point_id(self, entry_point_id: str) -> None:
        """
        Validate the entry point ID.
        :param entry_point_id: The entry point ID to validate.
        """
        error = ValueError("Invalid entryPointId")
        show = next(iter(self.service.get_shows_by_entry_point_id(entry_point_id)), {})

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
            rows = self.service.read_rows(
                "submissions",
                filters=[f"id = {uid}", f"entry_point_id = {entry_point_id}"],
            )
            if rows:
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
        request_rows = self.service.read_rows("requests", filters=[f"id = {uid}"])
        return self.service.read_rows(
            "songs",
            filters=[f"id = {next(iter(request_rows), {}).get('song_id')}"],
        )
