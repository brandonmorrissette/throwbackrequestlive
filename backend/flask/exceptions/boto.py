"""
This module provides a decorator to handle boto ClientError exceptions and raise HTTPException.
"""

import logging
from typing import Any, Callable, TypeVar

from botocore.exceptions import ClientError

from backend.flask.exceptions.http import HTTPException

T = TypeVar("T", bound=Callable[..., Any])


def raise_http_exception(func: T) -> T:
    """
    Decorator that wraps a function that make use of boto
    to catch ClientError exceptions and raise HTTPException.

    Args:
        func (function): The function to wrap.

    Returns:
        function: The wrapped function.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            exception = HTTPException(e.response["Error"]["Message"])
            exception.code = e.response["ResponseMetadata"]["HTTPStatusCode"]
            logging.error(
                "ClientError in %s: %s - %s",
                func.__qualname__,
                exception.code,
                exception.description,
            )
            raise exception from e

    return wrapper  # type: ignore
