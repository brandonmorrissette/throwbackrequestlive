from blueprints.blueprint import BaseBlueprint
from flask import current_app as app
from flask import jsonify, request


class AuthBlueprint(BaseBlueprint):

    def _register_routes(self):

        @self._blueprint.route("/login", methods=["POST"])
        def login():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            session = data.get("session")
            password_reset = data.get("password_reset")

            if not username or not password:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Username and password are required",
                        }
                    ),
                    400,
                )

            try:
                if password_reset:
                    response = self._service.reset_password(username, password, session)
                else:
                    response = self._service.authenticate_user(username, password)

                return (
                    jsonify(
                        {
                            "success": True,
                            "token": response["token"],
                            "error": response.get("error"),
                            "session": response.get("session"),
                        }
                    ),
                    200,
                )

            except Exception as e:
                app.logger.error(f"Error during Cognito authentication: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
