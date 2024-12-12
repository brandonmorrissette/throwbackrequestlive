from flask import Blueprint as FlaskBlueprint


class BaseBlueprint:
    def __init__(self, app, service=None, url_prefix="/api"):
        """
        Base class for all blueprints.

        :param app: Flask application instance
        :param service: Optional service for the blueprint
        :param url_prefix: URL prefix for the blueprint routes
        """
        self._app = app
        self._service = service
        self._blueprint = FlaskBlueprint(self.__class__.__name__.lower(), __name__)
        self._register_routes()
        self._app.register_blueprint(self._blueprint, url_prefix=url_prefix)

    def _register_routes(self):
        """
        Register routes for the blueprint.
        This should be overridden by child classes.
        """
        raise NotImplementedError("Child classes must implement _register_routes.")
