"""
This module defines the ShowBlueprintShowBlue class and related functions
for handling show related public routes in a Flask application.
"""

from typing import Any, Tuple

from flask import request

from backend.flask.blueprints.data import DataBlueprint
from backend.flask.services.data import DataService


class ShowBlueprint(DataBlueprint):
    """
    Blueprint for handling show related routes.
    """

    _service: DataService

    def register_routes(self) -> None:
        """
        Register routes for show operations.
        """

        # Public route
        @self.route("/tables/shows/rows", methods=["GET"])
        def read_shows() -> Tuple[Any, int]:
            """
            Read rows from the 'shows' table.
            :return: JSON response with the rows.
            """
            return self._get_rows("shows", request)
