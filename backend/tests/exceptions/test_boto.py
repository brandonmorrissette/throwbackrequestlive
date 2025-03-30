# pylint: disable=missing-function-docstring, missing-module-docstring, missing-class-docstring
import pytest
from botocore.exceptions import ClientError

from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.exceptions.http import HTTPException

ERROR = {"Message": "An error occurred"}
METADATA = {"HTTPStatusCode": 400}

CLIENT_ERROR = ClientError(
    error_response={
        "Error": ERROR,
        "ResponseMetadata": METADATA,
    },
    operation_name="TestOperation",
)


@raise_http_exception
def mock_function():
    raise CLIENT_ERROR


def test_given_function_doesnt_raise_error_when_invoked_then_return_value():
    @raise_http_exception
    def successful_mock_function():
        return "Success"

    result = successful_mock_function()
    assert result == "Success"


def test_given_function_raises_client_error_when_invoked_then_http_exception_reraised():
    with pytest.raises(HTTPException) as e:
        mock_function()

    assert e.value.description == ERROR["Message"]
    assert e.value.code == METADATA["HTTPStatusCode"]
