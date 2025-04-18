"""
Entry point related routes for the Flask application.
This module defines the EntryPointBlueprint class and related functions
"""

from flask import request
from werkzeug.wrappers.response import Response

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.services.entrypoint import EntryPointService


class EntryPointBlueprint(Blueprint):
    """
    Blueprint for handling entry point related routes.
    """

    _service: EntryPointService

    def __init__(
        self,
        service: EntryPointService,
        import_name: str | None = None,
        url_prefix: str | None = None,
    ) -> None:
        """
        Initialize the EntryPointBlueprint.

        :param session_factory: factory for creating sessions
        :param import_name: (Optional) Import name of the module
        :param url_prefix: (Optional) URL prefix for the blueprint routes
        """
        super().__init__(import_name, service, url_prefix)

    def register_routes(self) -> None:
        """
        Register routes for entry point operations.
        """

        @self.route("/entrypoint", methods=["GET"])
        def start_session() -> Response:
            """
            Establishes session for a provided entrypoint.
            :return: JSON response with the authentication token.
            """
            return self._service.start_session(request.args.get("entryPointId", ""))

        @self.route("/validate", methods=["GET"])
        def validate() -> Response:
            """ "
            Validates the session for a provided entrypoint.
            :return: Success repsonse if session is valid, otherwise error.
            """
            return self._service.validate_session()
