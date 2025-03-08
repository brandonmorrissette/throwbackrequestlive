"""
This module provides simple error mocks for testing purposes.
"""

from botocore.exceptions import ClientError

ERROR_MESSAGE = "error_message"
STATUS_CODE = 400
CLIENT_ERROR = ClientError(
    {
        "Error": {"Message": ERROR_MESSAGE},
        "ResponseMetadata": {"HTTPStatusCode": STATUS_CODE},
    },
    "operation_name",
)
