"""
This module defines the ShowBlueprintShowBlue class and related functions
for handling show related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import jsonify, request

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.decorators.auth import restrict_access
from backend.flask.services.entrypoint import EntryPointService


class ShowBlueprint(DataBlueprint):
    """
    Blueprint for handling show related routes.
    """

    _service: EntryPointService

    def register_routes(self) -> None:
        """
        Register routes for show operations.
        """

        @self.route("/tables/shows/rows", methods=["GET"])
        def read_shows() -> Tuple[Any, int]:
            """
            Read rows from the 'shows' table.
            :return: JSON response with the rows.
            """
            return self._get_rows("shows", request)

        @self.route("/tables/shows", methods=["POST"])
        @restrict_access(["superuser"])
        def insert_show() -> Tuple[Any, int]:
            """
            Insert rows into the 'shows' table.
            :return: JSON response with the result of the operation.
            """
            data = request.get_json()
            if not data:
                return {"message": "No data provided"}, 400

            entry_point_id = self._service.create_entry_point(
                "https://www.throwbackrequestlive.com"
            )

            data["entry_point_id"] = entry_point_id

            self._service.insert_rows("shows", [data])
            return jsonify({"success": True}), 201
