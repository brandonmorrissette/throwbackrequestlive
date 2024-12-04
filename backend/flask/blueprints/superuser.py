import secrets
import string

from blueprints.blueprint import BaseBlueprint
from flask import Blueprint, jsonify, request


class SuperuserBlueprint(BaseBlueprint):
    def _register_routes(self):

        @self._blueprint.route("/users", methods=["GET"])
        def list_users():
            try:
                users = self._service.list_users()
                return jsonify(users), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/users", methods=["POST"])
        def add_user():
            data = request.get_json()
            email = data["email"]
            username = data.get("username", "").strip() or email
            groups = data.get("groups", [])

            try:
                self._service.add_user(email, username, groups)
                return jsonify({"message": f"User {email} created successfully."}), 201
            except Exception as e:
                return jsonify({"message": str(e)}), 400

        @self._blueprint.route("/users/<username>", methods=["PUT"])
        def update_user(username):
            data = request.get_json()
            email = data.get("email")
            groups = data.get("groups", [])

            if not email:
                return jsonify({"message": "Email is required"}), 400

            try:
                self._service.update_user(username, email, groups)
                return (
                    jsonify({"message": f"User {username} updated successfully."}),
                    200,
                )
            except Exception as e:
                return jsonify({"message": str(e)}), 400

        @self._blueprint.route("/users/<username>", methods=["DELETE"])
        def delete_user(username):
            try:
                self._service.delete_user(username)
                return (
                    jsonify({"message": f"User {username} deleted successfully."}),
                    200,
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self._blueprint.route("/groups", methods=["GET"])
        def list_groups():
            try:
                groups = self._service.list_groups()
                return jsonify(groups), 200
            except Exception as e:
                return jsonify({"message": str(e)}), 500

    def generate_temp_password(self):
        characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(characters) for _ in range(12))
