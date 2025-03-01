from functools import wraps

from flask import current_app as app
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from werkzeug.exceptions import HTTPException


def restrict_access(groups):
    """
    Decorator to restrict access to endpoints based on user groups.

    Args:
        groups (list): List of groups that are allowed to access the endpoint.

    Returns:
        function: The decorated function which checks for group membership.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            """
            Wrapper function to verify JWT and check group membership.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Raises:
                HTTPException: If JWT verification fails or user is not in the required groups.

            Returns:
                function: The original function if access is granted.
            """
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                app.logger.debug(f"JWT Claims: {claims}")
            except Exception as e:
                app.logger.error(f"JWT verification failed: {e}")
                http_exception = HTTPException("Unauthorized")
                http_exception.code = 401
                raise http_exception

            if not any(group in claims.get("groups", []) for group in groups):
                app.logger.warning(
                    f"User is not in any of the required groups: {groups}."
                )
                http_exception = HTTPException("Forbidden")
                http_exception.code = 403
                raise http_exception

            return fn(*args, **kwargs)

        return wrapper

    return decorator
