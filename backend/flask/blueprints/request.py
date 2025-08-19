"""
This module defines the RequestBlueprint class and related functions
for handling request related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import current_app as app
from flask import jsonify, make_response, redirect, request, send_file, url_for
from werkzeug.exceptions import BadRequest

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

        @self.route("/requests/redirect/<string:show_hash>", methods=["GET"])
        def redirect_request(show_hash: str) -> Tuple[Any, int]:
            """
            Redirects to the request page for a specific show.
            """
            return self._service.redirect(show_hash), 302

        @self.route("/requests", methods=["PUT"])
        def write_request() -> Tuple[Any, int]:
            """
            Writes a new row in the 'requests' table.
            :return: JSON response with the result of the operation.
            """
            try:
                song_request = request.get_json()
                app.logger.debug(f"Received data for writing request: {song_request}")
            except BadRequest as e:
                app.logger.error(f"Bad request: {e}")
                return jsonify({"error": "Invalid JSON data."}), 400

            show_hash = request.cookies.get("throwbackRequestLiveShowHash")
            if show_hash == "DEMO":
                return make_response(redirect(url_for("demoblueprint.write_request")))

            return self._service.write_request(song_request), 201

        @self.route("/requests/count", methods=["GET"])
        def get_requests_count() -> Tuple[Any, int]:
            """
            Returns the count of requests for the songs.

            :return: JSON response with the count of requests.
            """
            return self._service.get_requests_counts(), 200
