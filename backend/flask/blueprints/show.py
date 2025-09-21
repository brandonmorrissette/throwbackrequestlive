"""
This module defines the ShowBlueprintShowBlue class and related functions
for handling show related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import current_app as app
from flask import jsonify, request

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.decorators.auth import restrict_access
from backend.flask.services.show import ShowService


class ShowBlueprint(DataBlueprint):
    """
    Blueprint for handling show related routes.
    """

    _service: ShowService

    def register_routes(self) -> None:
        """
        Register routes for show operations.
        """

        @self.route("/shows", methods=["GET"])
        def read_shows() -> Tuple[Any, int]:
            """
            Read rows from the 'shows' table.
            """
            return jsonify(self._service.get_shows()), 200

        @self.route("/shows", methods=["POST"])
        @restrict_access(["superuser"])
        def insert_show() -> Tuple[Any, int]:
            """
            Insert rows into the 'shows' table.
            :return: JSON response with the result of the operation.
            """
            show = request.get_json()
            app.logger.info(f"Show received to insert: {show}")
            if not show:
                return {"message": "No data provided"}, 400

            self._service.insert_show(show)

            return jsonify({"success": True}), 201

        @self.route("/shows/upcoming", methods=["GET"])
        def get_upcoming_shows() -> Tuple[Any, int]:
            """
            Get upcoming shows.
            :return: JSON response with the upcoming shows.
            """
            return self._service.get_upcoming_shows(), 200
