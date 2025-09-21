"""
This module defines the DemoBlueprint class and related functions
for handling demo related public routes in a Flask application.
"""
import uuid
from datetime import datetime
from typing import Any, Tuple

from flask import make_response, request, send_file, jsonify, current_app as app

from backend.flask.blueprints.request import RequestBlueprint
from backend.flask.services.demo import DemoService


class DemoBlueprint(RequestBlueprint):
    """
    Blueprint for handling demo-related routes.
    """

    _service: DemoService

    def register_routes(self) -> None:
        """
        Register routes for demo operations.
        """

        @self.route("/demo", methods=["GET"])
        def demo() -> Tuple[Any, int]:
            """
            Returns a demo response.
            :return: JSON response with the demo data.
            """
            return self._service.redirect("DEMO")

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

        @self.route("/api/requests/DEMO", methods=["POST"])
        def write_request() -> Tuple[Any, int]:
            """
            Writes a new row in the 'requests' table.
            :return: JSON response with the result of the operation.
            """
            song_request = request.get_json()

            song_request["request_time"] = datetime.now().isoformat()
            song_request["id"] = uuid.uuid4().hex
            self._service.write_request(song_request)

            response = make_response(jsonify(song_request), 201)
            response.set_cookie(
                "totalRequestLiveRequestId",
                song_request["id"],
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response

        @self.route("/api/requests/counts/DEMO", methods=["GET"])
        def get_requests_counts() -> Tuple[Any, int]:
            """
            Gets the count of requests for the demo show.
            """
            app.logger.info("Getting request counts for DEMO show.")
            return jsonify(self._service.get_requests_counts()), 200