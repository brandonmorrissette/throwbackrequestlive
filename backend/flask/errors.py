from flask import jsonify
from sqlalchemy.exc import OperationalError
import logging

def register_error_handlers(app):
    @app.errorhandler(OperationalError)
    def handle_db_error(error):
        logging.error("Database operation failed: %s", error)
        response = {
            "status": "error",
            "message": "The database is currently unavailable."
        }
        return jsonify(response), 503
