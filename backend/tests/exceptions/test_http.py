# pylint: disable=missing-function-docstring, missing-module-docstring
from flask import Flask

from backend.flask.exceptions.http import HTTPException

app = Flask(__name__)


def test_given_status_code_when_http_exception_raised_then_code_added_to_response():
    with app.test_request_context():
        exception = HTTPException(description="An error occurred")
        exception.code = 400
        response = exception.get_response()

        assert response.status_code == 400
        assert response.json == {"error": "An error occurred", "status": 400}


def test_given_no_status_code_when_http_exception_then_return_500_with_response():
    with app.test_request_context():
        exception = HTTPException(description="An error occurred")
        response = exception.get_response()

        assert response.status_code == 500
        assert response.json == {"error": "An error occurred", "status": None}
