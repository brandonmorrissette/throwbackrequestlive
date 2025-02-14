from flask import jsonify
from werkzeug.exceptions import HTTPException as FlaskHTTPException


class HTTPException(FlaskHTTPException):

    def get_response(self, environ=None):
        """Override to return JSON response instead of HTML"""

        response = jsonify({"error": self.description, "status": self.code})
        response.status_code = self.code if self.code is not None else 500
        return response
