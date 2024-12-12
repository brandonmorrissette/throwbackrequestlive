from functools import wraps

from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            app.logger.debug(f"JWT Claims: {claims}")
        except Exception as e:
            app.logger.error(f"JWT verification failed: {e}")
            return jsonify({"error": "Unauthorized"}), 401

        if "admin" not in claims.get("groups", []):
            app.logger.warning("User is not in admin group.")
            return jsonify({"error": "Forbidden"}), 403

        return fn(*args, **kwargs)

    return wrapper
