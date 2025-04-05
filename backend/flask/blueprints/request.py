"""
This module defines the RequestBlueprint class and related functions
for handling request related public routes in a Flask application.
"""

from datetime import datetime
from typing import Any, Tuple

from flask import current_app as app
from flask import jsonify, request

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.services.data import DataService


class RequestBlueprint(DataBlueprint):
    """
    Blueprint for handling request-related routes.
    """

    _service: DataService

    def register_routes(self) -> None:
        """
        Register routes for request operations.
        """

        @self.route("/tables/requests/rows", methods=["PUT"])
        def write_request() -> Tuple[Any, int]:
            """
            Writes a new row in the 'requests' table.
            :return: JSON response with the result of the operation.
            """
            data = request.get_json()
            app.logger.debug(f"Received data for writing request: {data}")

            song_request = next(iter(data["rows"]), {})
            if not song_request:
                app.logger.error("No song request data found.")
                return jsonify({"error": "No song request data found."}), 400

            uid = request.cookies.get("uid")
            song_request["request_time"] = datetime.now().isoformat()
            song_request["id"] = uid
            song_request["show_id"] = request.cookies.get("showId")

            self._service.insert_rows("requests", [song_request])

            results = self._service.insert_rows(
                "submissions",
                [
                    {
                        "id": uid,
                        "entry_point_id": request.cookies.get("entryPointId", ""),
                    }
                ],
            )

            return jsonify(results), 200
