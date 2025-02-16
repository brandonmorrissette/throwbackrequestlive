import logging

from botocore.exceptions import ClientError
from exceptions.http import HTTPException


def raise_http_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            exception = HTTPException(e.response["Error"]["Message"])
            exception.code = e.response["ResponseMetadata"]["HTTPStatusCode"]
            logging.error(
                f"Error in {func.__qualname__}: {exception.code} - {exception.description}"
            )
            raise exception

    return wrapper
