# pylint: disable=redefined-outer-name, protected-access, missing-function-docstring, missing-module-docstring
from typing import Generator
from unittest.mock import patch

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException

from backend.flask.decorators.auth import restrict_access


@pytest.fixture(scope="module")
def app() -> Generator[Flask, None, None]:
    app = Flask(__name__)
    yield app


def test_given_valid_jwt_and_group_when_access_endpoint_then_access_granted(
    app: Flask,
) -> None:
    @restrict_access(["superuser"])
    def mock_endpoint() -> str:
        return "Success"

    with app.test_request_context():
        with patch(
            "backend.flask.decorators.auth.verify_jwt_in_request"
        ) as mock_verify_jwt, patch(
            "backend.flask.decorators.auth.get_jwt",
            return_value={"groups": ["superuser"]},
        ):
            response = mock_endpoint()
            mock_verify_jwt.assert_called_once()
            assert response == "Success"


def test_given_invalid_jwt_when_access_endpoint_then_unauthorized_raised(
    app: Flask,
) -> None:
    @restrict_access(["superuser"])
    def mock_endpoint() -> str:
        return "Success"

    with app.test_request_context():
        with patch(
            "backend.flask.decorators.auth.verify_jwt_in_request",
            side_effect=Exception("Invalid JWT"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                mock_endpoint()
            assert exc_info.value.code == 401


def test_given_valid_jwt_but_no_group_when_access_endpoint_then_forbidden_raised(
    app: Flask,
) -> None:
    @restrict_access(["superuser"])
    def mock_endpoint() -> str:
        return "Success"

    with app.test_request_context():
        with patch(
            "backend.flask.decorators.auth.verify_jwt_in_request"
        ) as mock_verify_jwt, patch(
            "backend.flask.decorators.auth.get_jwt", return_value={"groups": ["user"]}
        ):
            with pytest.raises(HTTPException) as exc_info:
                mock_endpoint()
            mock_verify_jwt.assert_called_once()
            assert exc_info.value.code == 403
