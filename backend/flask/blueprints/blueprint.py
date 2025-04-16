"""
Base blueprint module for defining common blueprint functionality.
"""

from typing import Any, Optional

from flask import Blueprint as FlaskBlueprint


class Blueprint(FlaskBlueprint):
    """
    Base class for all blueprints.
    """

    def __init__(
        self,
        import_name: Optional[str] = None,
        service: Optional[Any] = None,
        url_prefix: Optional[str] = None,
    ) -> None:
        """
        Initialize the blueprint.

        :param import_name: Import name of the module
        :param service: Optional service for the blueprint
        :param url_prefix: URL prefix for the blueprint routes
        """
        name = self.__class__.__name__.lower()
        if not import_name:
            import_name = name

        super().__init__(name, import_name, url_prefix=url_prefix)
        self._service = service
        self.register_routes()

    def register_routes(self) -> None:
        """
        Register routes for the blueprint.
        This should be overridden by child classes.
        """
        raise NotImplementedError("Child classes must implement _register_routes.")
