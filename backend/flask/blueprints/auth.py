"""
This module contains the AuthBlueprint class which handles authentication-related routes.
"""

from typing import Any, Tuple

from blueprints.blueprint import Blueprint
from flask import jsonify, request
from services.auth import AuthService


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
