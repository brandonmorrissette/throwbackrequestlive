from blueprints.blueprint import BaseBlueprint
from flask import current_app as app
from flask import jsonify, request
from services.auth import AuthService


class AuthBlueprint(BaseBlueprint):
    _service: AuthService

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
