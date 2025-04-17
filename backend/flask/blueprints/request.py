"""
This module defines the RequestBlueprint class and related functions
for handling request related public routes in a Flask application.
"""

from datetime import datetime
from typing import Any, Tuple

from flask import current_app as app
from flask import jsonify, make_response, redirect, request, send_file, url_for
from werkzeug.wrappers.response import Response

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.services.request import RequestService


class RequestBlueprint(DataBlueprint):
    """
    Blueprint for handling request-related routes.
    """

    _service: RequestService

    def register_routes(self) -> None:
        """
        Register routes for request operations.
        """

        @self.route("/api/requests", methods=["PUT"])
        def write_request() -> Tuple[Any, int]:
            """
            Writes a new row in the 'requests' table.
            :return: JSON response with the result of the operation.
            """
            data = request.get_json()
            app.logger.debug(f"Received data for writing request: {data}")

            if not data:
                app.logger.error("No song request data found.")
                return jsonify({"error": "No song request data found."}), 400

            uid = request.cookies.get("uid")
            data["request_time"] = datetime.now().isoformat()
            data["id"] = uid
            data["show_id"] = request.cookies.get("showId")

            self._service.insert_rows("requests", [data])

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

        @self.route("/api/requests/count", methods=["GET"])
        def get_request_count_by_show_id() -> Tuple[Any, int]:
            """
            Returns the count of requests for a song.
            :return: JSON response with the count of requests.
            """
            show_id = request.args.get("showId")
            app.logger.debug(f"Received show ID for request count: {show_id}")
            if not show_id:
                app.logger.error("No show ID provided in request.")
                return jsonify({"error": "No show ID provided."}), 400

            return self._service.get_request_count_by_show_id(show_id), 200

        @self.route("/demo", methods=["GET"])
        def demo() -> Response:
            """
            Returns a demo response.
            :return: JSON response with the demo data.
            """

            demo_entry_point_id = self._service.get_demo_entry_point_id()
            app.logger.info(f"Recreating a demo request. {demo_entry_point_id}")
            response = make_response(
                redirect(url_for("renderblueprint.render_request"))
            )

            self._service.set_session_cookies(response)
            response.set_cookie(
                "entryPointId",
                demo_entry_point_id,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                "showId",
                str(
                    next(
                        iter(
                            self._service.get_shows_by_entry_point_id(
                                demo_entry_point_id
                            )
                        )
                    ).get("id")
                ),
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response

        @self.route("/qr", methods=["GET"])
        def demo_qr():
            """
            Returns a demo QR code response.
            :return: JSON response with the demo QR code data.
            """
            return send_file(
                self._service.get_demo_qr(),
                mimetype="image/png",
                as_attachment=False,
                download_name="qr.png",
            )
