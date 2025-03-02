"""
Blueprint module for rendering static HTML files for different routes.
"""

from blueprints.blueprint import BaseBlueprint
from flask import Response
from flask import current_app as app


class RenderBlueprint(BaseBlueprint):
    """
    Blueprint for rendering static HTML files for different routes.
    """

    def _register_routes(self) -> None:
        """
        Register routes for rendering static HTML files.
        """

        @self._blueprint.route("/request")
        def render_request() -> Response:
            """
            Render the request page.
            :return: The request page HTML file.
            """
            return app.send_static_file("index.html")

        @self._blueprint.route("/admin")
        def render_admin() -> Response:
            """
            Render the admin page.
            :return: The admin page HTML file.
            """
            return app.send_static_file("index.html")

        @self._blueprint.route("/login")
        def render_login() -> Response:
            """
            Render the login page.
            :return: The login page HTML file.
            """
            return app.send_static_file("index.html")

        @self._blueprint.route("/", defaults={"path": ""})
        @self._blueprint.route("/<path:path>")
        def render_main(path: str) -> Response:  # pylint: disable=unused-argument
            """
            Render the main page for any other routes.
            :param path: The path of the requested route.
            :return: The main page HTML file.
            """
            return app.send_static_file("index.html")
