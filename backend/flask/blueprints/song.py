"""
This module defines the SongBlueprint class and related functions
for handling song related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import request

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.services.data import DataService


class SongBlueprint(DataBlueprint):
    """
    Blueprint for handling song related routes.
    """

    _service: DataService

    def register_routes(self) -> None:
        """
        Register routes for song operations.
        """

        @self.route("/tables/songs/rows", methods=["GET"])
        def read_songs() -> Tuple[Any, int]:
            """
            Read rows from the 'songs' table.
            :return: JSON response with the rows.
            """
            return self._get_rows("songs", request)
