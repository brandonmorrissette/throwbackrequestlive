from flask import Blueprint
from flask import current_app as app

render_bp = Blueprint("render", __name__)


@render_bp.route("/vote")
def render_vote():
    return app.send_static_file("index.html")


@render_bp.route("/admin")
def render_admin():
    return app.send_static_file("index.html")


@render_bp.route("/login")
def render_login():
    return app.send_static_file("index.html")


@render_bp.route("/", defaults={"path": ""})
@render_bp.route("/<path:path>")
def render_main(path):
    return app.send_static_file("index.html")
