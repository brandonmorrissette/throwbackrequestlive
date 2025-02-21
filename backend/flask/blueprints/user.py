from blueprints.blueprint import BaseBlueprint
from decorators.auth import restrict_access
from flask import current_app as app
from flask import jsonify, request
from services.cognito import CognitoService


class UserBlueprint(BaseBlueprint):
    _service: CognitoService

    def _register_routes(self):

        @self._blueprint.route("/users", methods=["GET"])
        @restrict_access(["superuser"])
        def read_rows():
            users = self._service.read_rows()
            app.logger.debug(f"Listing users: {users}")
            return jsonify(users), 200

        @self._blueprint.route("/users", methods=["PUT"])
        @restrict_access(["superuser"])
        def write_rows():
            response = request.json
            app.logger.debug(f"Writing users: {response}")
            self._service.write_rows(response["rows"])
            return jsonify({"message": "Success"}), 200
