"""
This module contains the AuthBlueprint class which handles authentication related routes.
"""

from typing import Any, Dict, Optional, Tuple, Union

from flask import current_app, jsonify, request

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.services.auth import AuthService


class AuthBlueprint(Blueprint):
    """
    Blueprint for handling authentication related routes.
    """

    _service: AuthService

    def __init__(
        self,
        service: AuthService,
        import_name: Optional[str] = None,
        url_prefix: Optional[str] = None,
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
            current_app.logger.info("Login request received")
            data: Dict[str, Union[str, None]] = request.get_json()
            username: Optional[str] = data.get("username")
            password: Optional[str] = data.get("password")
            password_reset: Optional[bool] = bool(data.get("password_reset"))

            session: str = str(data.get("session", ""))

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
                response: Dict[str, Union[str, None]] = self._service.reset_password(
                    username, password, session
                )
            else:
                response: Dict[str, Union[str, None]] = self._service.authenticate_user(
                    username, password
                )

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
