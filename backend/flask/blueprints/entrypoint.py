"""
Entry point related routes for the Flask application.
This module defines the EntryPointBlueprint class and related functions
"""

from flask import request

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.session.session import SessionFactory


class EntryPointBlueprint(Blueprint):
    """
    Blueprint for handling entry point related routes.
    """

    _session_factory: SessionFactory

    def __init__(
        self,
        session_factory: SessionFactory,
        import_name: str | None = None,
        url_prefix: str | None = None,
    ) -> None:
        """
        Initialize the EntryPointBlueprint.

        :param session_factory: factory for creating sessions
        :param import_name: (Optional) Import name of the module
        :param url_prefix: (Optional) URL prefix for the blueprint routes
        """
        super().__init__(import_name, url_prefix)
        self._session_factory = session_factory

    def register_routes(self) -> None:
        """
        Register routes for entry point operations.
        """

        @self.route("/entrypoint", methods=["GET"])
        def start_session():
            """
            Establishes session for a provided entrypoint.
            :return: JSON response with the authentication token.
            """
            entry_point_id = request.args.get("entryPointId", "")
            return self._session_factory.start(entry_point_id)

        @self.route("/validate", methods=["GET"])
        def validate():
            """ "
            Validates the session for a provided entrypoint.
            :return: Success repsonse if session is valid, otherwise error.
            """
            return self._session_factory.validate_session()
