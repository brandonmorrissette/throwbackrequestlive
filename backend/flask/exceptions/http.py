"""
This module defines a custom HTTPException class that returns a JSON response
instead of the default HTML response provided by Flask.
"""

from typing import Any, Optional

from flask import jsonify
from flask.wrappers import Response
from werkzeug.exceptions import HTTPException as FlaskHTTPException


class HTTPException(FlaskHTTPException):
    """
    Custom HTTPException that returns a JSON response instead of HTML.

    Attributes:
        description (str): The error message.
        code (int): The HTTP status code.
    """

    description: str
    code: Optional[int]

    def get_response(
        # pylint: disable=unused-argument
        self,
        environ: Optional[dict] = None,
        scope: Optional[Any] = None,
        receive: Optional[Any] = None,
    ) -> Response:
        """
        Override to return JSON response instead of HTML.

        Args:
            environ (dict, optional): The WSGI environment. Defaults to None.
            scope (Any, optional): ASGI scope. Defaults to None.
            receive (Any, optional): ASGI receive function. Defaults to None.

        Returns:
            Response: The Flask response object with JSON data.
        """
        response = jsonify({"error": self.description, "status": self.code})
        response.status_code = self.code if self.code is not None else 500
        return response
