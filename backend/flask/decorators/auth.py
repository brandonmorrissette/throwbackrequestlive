from functools import wraps

from flask import current_app as app
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def restrict_access(groups):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                app.logger.debug(f"JWT Claims: {claims}")
            except Exception as e:
                app.logger.error(f"JWT verification failed: {e}")
                return jsonify({"error": "Unauthorized"}), 401

            if not any(group in claims.get("groups", []) for group in groups):
                app.logger.warning(
                    f"User is not in any of the required groups: {groups}."
                )
                return jsonify({"error": "Forbidden"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
