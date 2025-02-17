import json
from functools import wraps

from blueprints.blueprint import BaseBlueprint
from decorators.auth import restrict_access
from flask import Flask
from flask import current_app as app
from flask import jsonify, request
from services.data import DataService, get_json_provider_class


def override_json_provider(provider):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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


class DataBlueprint(BaseBlueprint):
    _service: DataService

    def _register_routes(self):
        @self._blueprint.route("/tables", methods=["GET"])
        @restrict_access(["superuser"])
        def list_tables():
            try:
                app.logger.debug("Listing tables")
                tables = self._service.list_tables()
                app.logger.debug(f"Tables: {tables}")
                return jsonify(list(tables)), 200
            except Exception as e:
                app.logger.error(f"Error listing tables: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>", methods=["GET"])
        @restrict_access(["superuser"])
        @override_json_provider(get_json_provider_class())
        def get_table(table_name):
            try:
                app.logger.debug(f"Getting table {table_name}")
                self._service.validate_table_name(table_name)
                table = self._service.get_table(table_name)
                app.logger.debug(f"Table {table_name}: {table}")

                return jsonify(table), 200
            except Exception as e:
                app.logger.error(f"Error getting table {table_name}: {e}")
                return jsonify({"error": str(e)}), 500

        # Public route
        @self._blueprint.route("/tables/shows/rows", methods=["GET"])
        def read_shows():
            return read_rows("shows")

        @self._blueprint.route("/tables/<table_name>/rows", methods=["GET"])
        @restrict_access(["superuser"])
        def read_rows(table_name):
            return self._get_rows(table_name, request)

        @self._blueprint.route("/tables/<table_name>/rows", methods=["PUT"])
        @restrict_access(["superuser"])
        def write_rows(table_name):
            data = request.get_json()
            rows = data.get("rows", [])
            app.logger.debug(f"Writing rows to {table_name}")
            # try:
            self._service.validate_table_name(table_name)
            result = self._service.write_rows(table_name, rows)
            return jsonify(result), 200
            # except Exception as e:
            #     app.logger.error(f"Error writing rows: {e}")
            #     return jsonify({"error": str(e)}), 500

    def _get_rows(self, table_name, request):
        filters = request.args.get("filters")
        if filters:
            filters = json.loads(filters)
            app.logger.debug(f"Filters: {filters}")

        try:
            self._service.validate_table_name(table_name)
            app.logger.debug(f"Getting rows from {table_name}")
            rows = self._service.read_rows(table_name, filters)
            app.logger.debug(f"First 10 Rows: {rows[:10]}")
            return jsonify(rows), 200
        except Exception as e:
            app.logger.error(f"Error fetching rows: {e}")
            return jsonify({"error": str(e)}), 500
