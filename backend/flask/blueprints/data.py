"""
This module defines the DataBlueprint class and related functions
for handling data-related routes in a Flask application.
"""

import json
from functools import wraps
from typing import Any, Callable, Tuple

from flask import Flask, Request
from flask import current_app as app
from flask import jsonify, request

from backend.flask.blueprints.blueprint import Blueprint
from backend.flask.decorators.auth import restrict_access
from backend.flask.services.data import DataService, get_json_provider_class


def override_json_provider(provider: Callable) -> Callable:
    """
    Decorator to override the JSON provider for a route.
    :param provider: The JSON provider class to use.
    :return: The decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            app.logger.debug(f"Overriding JSON provider with {provider}")
            original_provider = app.json
            app_instance = Flask(__name__)
            app.json = provider(app_instance)
            try:
                return func(*args, **kwargs)
            finally:
                app.json = original_provider

        return wrapper

    return decorator


class DataBlueprint(Blueprint):
    """
    Blueprint for handling data-related routes.
    """

    _service: DataService

    def register_routes(self) -> None:
        """
        Register routes for data operations.
        """

        @self.route("/tables", methods=["GET"])
        @restrict_access(["superuser"])
        def list_tables() -> Tuple[Any, int]:
            """
            List all tables.
            :return: JSON response with the list of tables.
            """
            app.logger.debug("Listing tables")
            tables = self._service.list_tables()
            app.logger.debug(f"Tables: {tables}")
            return jsonify(list(tables)), 200

        @self.route("/tables/<table_name>", methods=["GET"])
        @restrict_access(["superuser"])
        @override_json_provider(get_json_provider_class())
        def get_table(table_name: str) -> Tuple[Any, int]:
            """
            Get details of a specific table.
            :param table_name: The name of the table.
            :return: JSON response with the table details.
            """
            app.logger.debug(f"Getting table {table_name}")
            self._service.validate_table_name(table_name)
            table = self._service.get_table(table_name)
            app.logger.debug(f"Table {table_name}: {table}")

            return jsonify(table), 200

        # Public route
        @self.route("/tables/shows/rows", methods=["GET"])
        def read_shows() -> Tuple[Any, int]:
            """
            Read rows from the 'shows' table.
            :return: JSON response with the rows.
            """
            return self._get_rows("shows", request)

        @self.route("/tables/<table_name>/rows", methods=["GET"])
        @restrict_access(["superuser"])
        def read_rows(table_name: str) -> Tuple[Any, int]:
            """
            Read rows from a specific table.
            :param table_name: The name of the table.
            :return: JSON response with the rows.
            """
            return self._get_rows(table_name, request)

        @self.route("/tables/<table_name>/rows", methods=["PUT"])
        @restrict_access(["superuser"])
        def write_rows(table_name: str) -> Tuple[Any, int]:
            """
            Write rows to a specific table.
            :param table_name: The name of the table.
            :return: JSON response with the result of the operation.
            """
            data = request.get_json()
            rows = data.get("rows", [])
            app.logger.debug(f"Writing rows to {table_name}")
            self._service.validate_table_name(table_name)
            result = self._service.write_rows(table_name, rows)
            return jsonify(result), 200

    def _get_rows(self, table_name: str, _request: Request) -> Tuple[Any, int]:
        """
        Helper method to get rows from a table with optional filters.
        :param table_name: The name of the table.
        :param request: The Flask request object.
        :return: JSON response with the rows.
        """
        filters = _request.args.get("filters")
        if filters:
            filters = json.loads(filters)
            app.logger.debug(f"Filters: {filters}")

        self._service.validate_table_name(table_name)
        app.logger.debug(f"Getting rows from {table_name}")
        rows = self._service.read_rows(table_name, filters)
        app.logger.debug(f"First 10 Rows: {rows[:10]}")
        return jsonify(rows), 200
