"""
This module defines the SongBlueprint class and related functions
for handling song related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import jsonify

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.services.song import SongService


class SongBlueprint(Blueprint):
    """
    Blueprint for handling song related routes.
    """

    _service: SongService

    def register_routes(self) -> None:
        """
        Register routes for song operations.
        """

        @self.route("/songs", methods=["GET"])
        def read_songs() -> Tuple[Any, int]:
            """
            Read all songs.
            """
            return jsonify(self._service.get_songs()), 200
