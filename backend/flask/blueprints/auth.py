"""
This module contains the AuthBlueprint class which handles authentication-related routes.
"""

from typing import Any, Tuple

from flask import jsonify, make_response, redirect, request, url_for

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.services.auth import AuthService


class AuthBlueprint(Blueprint):
    """
    Blueprint for handling authentication-related routes.
    """

    _service: AuthService

    def register_routes(self) -> None:
        """
        Register routes for authentication operations.
        """

        @self.route("/login", methods=["POST"])
        def login() -> Tuple[Any, int]:
            """
            Authenticate a user and return a token.
            :return: JSON response with the authentication token.
            """
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            session = data.get("session")
            password_reset = data.get("password_reset")

            if not username or not password:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Username and password are required",
                        }
                    ),
                    400,
                )

            if password_reset:
                response = self._service.reset_password(username, password, session)
            else:
                response = self._service.authenticate_user(username, password)

            return (
                jsonify(
                    {
                        "success": True,
                        "token": response["token"],
                        "error": response.get("error"),
                        "session": response.get("session"),
                    }
                ),
                200,
            )

        @self.route("/entry", methods=["POST"])
        def entry():
            """
            Establishes an entry point for establishing a session.
            :return: JSON response with the authentication token.
            """
            entry_id = request.get_json().get("entryId")
            if not self._service.read_rows(
                "entryPoints",
                filters=[f"id = '{entry_id}'"],
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Invalid entryPointId",
                            "code": 400,
                        }
                    ),
                    400,
                )

            uid = request.cookies.get("uid")
            if uid:
                rows = self._service.read_rows(
                    "submissions",
                    filters=[f"uid = '{uid}'"],
                )
                if rows:
                    return _handle_duplicate_submission(uid)

            uid = self._service.generate_uid(plain_text=[entry_id])
            access_key = self._service.generate_access_key()

            response = make_response(redirect(url_for("render_request")))

            response.set_cookie("uid", uid, httponly=True, secure=True, samesite="Lax")
            response.set_cookie(
                "accessKey", access_key, httponly=True, secure=True, samesite="Lax"
            )

            return response

        # This is use case specific. Consider a better way of handling.
        def _handle_duplicate_submission(uid):
            """
            Handle duplicate submission by redirecting to the main page."
            """

            redirect_args = _get_duplicate_submission(uid)
            return redirect(
                url_for(
                    "render_main",
                    song_name=next(iter(redirect_args), {}).get(
                        "song_name", "UNABLE TO RETRIEVE SONG NAME"
                    ),
                )
            )

        def _get_duplicate_submission(uid: str):
            """
            Get duplicate submission by uid.
            :param uid: The unique identifier for the submission.
            :return: JSON response with the duplicate submission details.
            """
            request_rows = self._service.read_rows(
                "requests", filters=[f"request_id = {uid}"]
            )
            return self._service.read_rows(
                "songs",
                filters=[f"song_id = {next(iter(request_rows), {}).get('song_id')}"],
            )
