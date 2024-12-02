import csv
import logging
import os
import secrets
import string
from datetime import datetime

import boto3
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, redirect, request
from service.auth_service import AuthService

bp = Blueprint("routes", __name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

auth_service = AuthService()
cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")


@app.route("/vote")
def render_vote():
    return app.send_static_file("index.html")


@app.route("/admin")
def render_admin():
    return app.send_static_file("index.html")


@app.route("/login")
def render_login():
    return app.send_static_file("index.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    session = data.get("session")
    password_reset = data.get("password_reset")

    if not username or not password:
        return (
            jsonify({"success": False, "error": "Username and password are required"}),
            400,
        )

    try:
        if password_reset:
            response = auth_service.reset_password(username, password, session)
        else:
            response = auth_service.authenticate_user(username, password)

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


@app.route("/api/vote", methods=["POST"])
def post_vote():
    vote_data = request.get_json()
    print("Vote data received:", vote_data)
    song_name = vote_data.get("song")
    return redirect(f"/?song={song_name}")


@bp.route("/api/shows", methods=["GET"])
def get_shows():
    shows = []
    file_path = os.path.join(os.path.dirname(__file__), "data", "shows.csv")
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            show_datetime = datetime.strptime(
                f"{row['date']} {row['time']}", "%m-%d-%Y %I:%M %p"
            )
            if show_datetime >= datetime.now():
                shows.append(
                    {
                        "name": row["name"],
                        "date": row["date"],
                        "time": row["time"],
                        "venue": row["venue"],
                        "street": row["street"],
                        "city": row["city"],
                        "state": row["state"],
                    }
                )
    return jsonify(shows)


@bp.route("/api/songs", methods=["GET"])
def get_songs():
    songs = []
    file_path = os.path.join(os.path.dirname(__file__), "data", "songs.csv")
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append(
                {
                    "band": row["Band"],
                    "song_name": row["Song Name"],
                    "total_votes": int(row["Total Votes"]),
                    "votes_per_show": int(row["Votes Per Show"]),
                }
            )
    return jsonify(songs)


@app.route("/api/users", methods=["GET"])
def list_users():
    try:
        response = cognito_client.list_users(UserPoolId=USER_POOL_ID)
        users = [
            {
                "username": user["Username"],
                "email": next(
                    (
                        attr["Value"]
                        for attr in user["Attributes"]
                        if attr["Name"] == "email"
                    ),
                    None,
                ),
                "groups": [
                    group["GroupName"]
                    for group in cognito_client.admin_list_groups_for_user(
                        Username=user["Username"], UserPoolId=USER_POOL_ID
                    )["Groups"]
                ],
            }
            for user in response["Users"]
        ]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_temp_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(characters) for _ in range(12))


@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json()
    email = data["email"]
    username = data.get("username", "").strip() or email
    groups = data.get("groups", [])

    logging.info(f"Creating user {email} with username {username} and groups {groups}")
    try:
        cognito_client.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
            TemporaryPassword=generate_temp_password(),
        )

        for group in groups:
            cognito_client.admin_add_user_to_group(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=username,
                GroupName=group,
            )

        return jsonify({"message": f"User {email} created successfully."}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route("/api/users/<username>", methods=["PUT"])
def update_user(username):
    data = request.get_json()
    email = data.get("email")
    groups = data.get("groups", [])

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        cognito_client.admin_update_user_attributes(
            UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
        )

        existing_groups = cognito_client.admin_list_groups_for_user(
            UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
            Username=username,
        )["Groups"]

        for group in existing_groups:
            cognito_client.admin_remove_user_from_group(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=username,
                GroupName=group["GroupName"],
            )

        for group in groups:
            cognito_client.admin_add_user_to_group(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=username,
                GroupName=group,
            )

        return jsonify({"message": f"User {username} updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route("/api/users/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        cognito_client.admin_delete_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
        )
        return jsonify({"message": f"User {username} deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/groups", methods=["GET"])
def list_groups():
    try:
        response = cognito_client.list_groups(
            UserPoolId=os.getenv("COGNITO_USER_POOL_ID")
        )
        groups = [group["GroupName"] for group in response["Groups"]]
        return jsonify(groups), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def render_main(path):
    return app.send_static_file("index.html")
