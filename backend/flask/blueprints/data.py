from blueprints.blueprint import BaseBlueprint
from decorators.auth import admin_required
from flask import current_app as app
from flask import jsonify, request


class DataBlueprint(BaseBlueprint):

    def _register_routes(self):

        @self._blueprint.route("/tables", methods=["GET"])
        @admin_required
        def list_tables():
            try:
                tables = self._service.list_tables()
                app.logger.debug(f"Tables: {tables}")
                return jsonify(list(tables)), 200
            except Exception as e:
                app.logger.error(f"Error listing tables: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>/columns", methods=["GET"])
        @admin_required
        def get_columns(table_name):
            try:
                self._service.validate_table_name(table_name)
                columns = self._service.get_columns(table_name)
                app.logger.debug(f"Columns: {columns}")
                return jsonify(columns), 200
            except Exception as e:
                app.logger.error(f"Error getting table columns: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>", methods=["GET"])
        @admin_required
        def read_rows(table_name):
            filters = request.args.get("filters")
            limit = request.args.get("limit")
            offset = request.args.get("offset")
            sort_by = request.args.get("sort_by")
            sort_order = request.args.get("sort_order", "asc")

            app.logger.debug(
                f"Filters: {filters}, Sort By: {sort_by}, Sort Order: {sort_order}, Limit: {limit}, Offset: {offset}"
            )

            try:
                self._service.validate_table_name(table_name)
                rows = self._service.read_rows(
                    table_name, filters, limit, offset, sort_by, sort_order
                )
                app.logger.debug(f"First 10 Rows: {rows[:10]}")
                return jsonify(rows), 200
            except Exception as e:
                app.logger.error(f"Error fetching rows: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>", methods=["PUT"])
        @admin_required
        def write_rows(table_name):
            data = request.get_json()
            rows = data.get("rows", [])
            app.logger.debug(f"Writing rows: {rows}")
            try:
                self._service.validate_table_name(table_name)
                result = self._service.write_rows(table_name, rows)
                return jsonify(result), 200
            except Exception as e:
                app.logger.error(f"Error writing rows: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/query", methods=["POST"])
        @admin_required
        def execute_query():
            data = request.get_json()
            query = data.get("query")
            params = data.get("params", {})
            try:
                result = self._service.execute_custom_query(query, params)
                return jsonify(result), 200
            except Exception as e:
                app.logger.error(f"Error executing query: {e}")
                return jsonify({"error": str(e)}), 500
