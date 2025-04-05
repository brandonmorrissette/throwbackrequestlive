"""
This module contains the AuthBlueprint class which handles authentication-related routes.
"""

from typing import Any, Tuple

from flask import jsonify, request

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.services.auth import AuthService


class AuthBlueprint(Blueprint):
    """
    Blueprint for handling authentication-related routes.
    """

    _service: AuthService

    def __init__(
        self,
        service: AuthService,
        import_name: str | None = None,
        url_prefix: str | None = None,
    ) -> None:
        """
        Initialize the AuthBlueprint.

        :param service: service for the blueprint
        :param import_name: (Optional) Import name of the module
        :param url_prefix: (Optional) URL prefix for the blueprint routes
        """
        super().__init__(import_name, service, url_prefix)

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
