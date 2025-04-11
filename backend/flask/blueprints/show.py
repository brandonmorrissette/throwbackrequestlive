"""
This module defines the ShowBlueprintShowBlue class and related functions
for handling show related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import current_app as app
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
            return jsonify(self._service.execute("SELECT * FROM shows")), 200

        @self.route("/tables/shows/rows", methods=["POST"])
        @restrict_access(["superuser"])
        def insert_show() -> Tuple[Any, int]:
            """
            Insert rows into the 'shows' table.
            :return: JSON response with the result of the operation.
            """
            show = next(iter(request.get_json().get("rows")), {})
            app.logger.info(f"Show received: {show}")
            if not show:
                return {"message": "No data provided"}, 400

            entry_point_id = self._service.create_entry_point()
            show["entry_point_id"] = entry_point_id

            self._service.insert_rows("shows", [show])

            self._service.create_qr_code(
                f"https://www.throwbackrequestlive.com/entrypoint?entryPointId={entry_point_id}",  # pylint: disable=line-too-long
                f"entrypoints/{show['name']}/",
            )

            return jsonify({"success": True}), 201

        @self.route("/shows/upcoming", methods=["GET"])
        def get_upcoming_shows() -> Tuple[Any, int]:
            """
            Get upcoming shows.
            :return: JSON response with the upcoming shows.
            """
            return (
                jsonify(
                    self._service.execute(
                        "SELECT * FROM shows WHERE start_time > NOW()::timestamp ORDER BY start_time ASC"  # pylint: disable=line-too-long
                    )
                ),
                200,
            )
