import logging

from botocore.exceptions import ClientError
from exceptions.http import HTTPException


def raise_http_exception(func):
    """
    Decorator that wraps a function that make use of boto to catch ClientError exceptions and raise HTTPException.

    Args:
        func (function): The function to wrap.

    Returns:
        function: The wrapped function.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            exception = HTTPException(e.response["Error"]["Message"])
            exception.code = e.response["ResponseMetadata"]["HTTPStatusCode"]
            logging.error(
                f"ClientError in {func.__qualname__}: {exception.code} - {exception.description}"
            )
            raise exception

    return wrapper
