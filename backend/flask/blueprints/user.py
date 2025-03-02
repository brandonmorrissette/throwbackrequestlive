"""
Blueprint module for handling user-related routes.
"""

from typing import Any, Tuple

from blueprints.blueprint import BaseBlueprint
from decorators.auth import restrict_access
from flask import current_app as app
from flask import jsonify, request
from services.cognito import CognitoService


class UserBlueprint(BaseBlueprint):
    """
    Blueprint for handling user-related routes.
    """

    _service: CognitoService

    def _register_routes(self) -> None:
        """
        Register routes for user operations.
        """

        @self._blueprint.route("/users", methods=["GET"])
        @restrict_access(["superuser"])
        def read_rows() -> Tuple[Any, int]:
            """
            List all users.
            :return: JSON response with the list of users.
            """
            users = self._service.read_rows()
            app.logger.debug(f"Listing users: {users}")
            return jsonify(users), 200

        @self._blueprint.route("/users", methods=["PUT"])
        @restrict_access(["superuser"])
        def write_rows() -> Tuple[Any, int]:
            """
            Write user data.
            :return: JSON response with the result of the operation.
            """
            response = request.json
            app.logger.debug(f"Writing users: {response}")
            if response and "rows" in response:
                self._service.write_rows(response["rows"])
            else:
                return (
                    jsonify({"message": "Invalid input, rows not found in request."}),
                    400,
                )
            return jsonify({"message": "Success"}), 200
