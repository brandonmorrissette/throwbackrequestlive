from blueprints.blueprint import BaseBlueprint
from flask import current_app as app


class RenderBlueprint(BaseBlueprint):

    def _register_routes(self):
        @self._blueprint.route("/request")
        def render_request():
            return app.send_static_file("index.html")

        @self._blueprint.route("/admin")
        def render_admin():
            return app.send_static_file("index.html")

        @self._blueprint.route("/login")
        def render_login():
            return app.send_static_file("index.html")

        @self._blueprint.route("/", defaults={"path": ""})
        @self._blueprint.route("/<path:path>")
        def render_main(path):
            return app.send_static_file("index.html")
