"""
A module for handling Flask application errors.
"""
import logging

from flask import jsonify
from sqlalchemy.exc import OperationalError

def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    """
    @app.errorhandler(OperationalError)
    def handle_db_error(error):
        """
        Handle database operational errors.
        """
        logging.error("Database operation failed: %s", error)
        response = {
            "status": "error",
            "message": "The database is currently unavailable."
        }
        return jsonify(response), 503
