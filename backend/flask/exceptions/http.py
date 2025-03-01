from flask import jsonify
from werkzeug.exceptions import HTTPException as FlaskHTTPException


class HTTPException(FlaskHTTPException):
    """
    Custom HTTPException that returns a JSON response instead of HTML.

    Attributes:
        description (str): The error message.
        code (int): The HTTP status code.
    """

    def get_response(self, environ=None):
        """
        Override to return JSON response instead of HTML.

        Args:
            environ (dict, optional): The WSGI environment. Defaults to None.

        Returns:
            Response: The Flask response object with JSON data.
        """
        response = jsonify({"error": self.description, "status": self.code})
        response.status_code = self.code if self.code is not None else 500
        return response
