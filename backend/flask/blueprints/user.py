from blueprints.blueprint import BaseBlueprint
from flask import current_app as app
from flask import jsonify, request


class UserBlueprint(BaseBlueprint):
    def _register_routes(self):

        @self._blueprint.route("/users", methods=["GET"])
        def read_rows():
            try:
                users = self._service.read_rows()
                app.logger.debug(f"Listing users: {users}")
                return jsonify(users), 200
            except Exception as e:
                app.logger.error(f"Error listing users: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/users", methods=["PUT"])
        def write_rows():
            try:
                response = request.json
                app.logger.debug(f"Writing users: {response}")
                self._service.write_rows(response["rows"])
                return jsonify({"message": "Success"}), 200
            except Exception as e:
                app.logger.error(f"Error writing users: {e}")
                return jsonify({"error": str(e)}), 500
