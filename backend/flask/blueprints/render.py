"""
Blueprint module for rendering static HTML files for different routes.
"""

from typing import Optional

from flask import Response
from flask import current_app as app

from backend.flask.blueprints.blueprint import Blueprint


class RenderBlueprint(Blueprint):
    """
    Blueprint for rendering static HTML files for different routes.
    """

    def register_routes(self) -> None:
        """
        Register routes for rendering static HTML files.
        """

        @self.route("/request")
        def render_request() -> Response:
            """
            Render the request page.
            :return: The request page HTML file.
            """
            return app.send_static_file("index.html")

        @self.route("/admin")
        def render_admin() -> Response:
            """
            Render the admin page.
            :return: The admin page HTML file.
            """
            return app.send_static_file("index.html")

        @self.route("/login")
        def render_login() -> Response:
            """
            Render the login page.
            :return: The login page HTML file.
            """
            return app.send_static_file("index.html")

        @self.route("/", defaults={"path": ""})
        @self.route("/<path:path>")
        def render_main(
            path: Optional[str] = None,  # pylint: disable=unused-argument
        ) -> Response:
            """
            Render the main page for any other routes.
            :param path: The path of the requested route.
            :return: The main page HTML file.
            """
            return app.send_static_file("index.html")
