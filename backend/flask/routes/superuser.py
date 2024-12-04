import secrets
import string

from flask import Blueprint, jsonify, request
from services.cognito_service import add_user as cognito_add_user
from services.cognito_service import delete_user as cognito_delete_user
from services.cognito_service import list_groups as cognito_list_groups
from services.cognito_service import list_users as cognito_list_users
from services.cognito_service import update_user as cognito_update_user

superuser_bp = Blueprint("superuser", __name__)


def generate_temp_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(characters) for _ in range(12))


@superuser_bp.route("/users", methods=["GET"])
def list_users():
    try:
        users = cognito_list_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@superuser_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    email = data["email"]
    username = data.get("username", "").strip() or email
    groups = data.get("groups", [])

    try:
        cognito_add_user(email, username, groups)
        return jsonify({"message": f"User {email} created successfully."}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@superuser_bp.route("/users/<username>", methods=["PUT"])
def update_user(username):
    data = request.get_json()
    email = data.get("email")
    groups = data.get("groups", [])

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        cognito_update_user(username, email, groups)
        return jsonify({"message": f"User {username} updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@superuser_bp.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        cognito_delete_user(username)
        return jsonify({"message": f"User {username} deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@superuser_bp.route("/groups", methods=["GET"])
def list_groups():
    try:
        groups = cognito_list_groups()
        return jsonify(groups), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
