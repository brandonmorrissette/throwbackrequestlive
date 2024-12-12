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
                return jsonify(columns), 200
            except Exception as e:
                app.logger.error(f"Error getting table columns: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>", methods=["GET"])
        @admin_required
        def fetch_rows(table_name):
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
                return jsonify(rows), 200
            except Exception as e:
                app.logger.error(f"Error fetching rows: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>", methods=["POST"])
        @admin_required
        def insert_row(table_name):
            data = request.get_json()
            try:
                self._service.validate_table_name(table_name)
                self._service.validate_columns(table_name, data.keys())
                self._service.create_row(table_name, data)
                return jsonify({"message": "Row inserted successfully."}), 201
            except Exception as e:
                app.logger.error(f"Error inserting row: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>/<row_id>", methods=["PUT"])
        @admin_required
        def update_row(table_name, row_id):
            data = request.get_json()
            try:
                self._service.validate_table_name(table_name)
                self._service.validate_columns(table_name, data.keys())
                self._service.update_row(table_name, row_id, data)
                return jsonify({"message": "Row updated successfully."}), 200
            except Exception as e:
                app.logger.error(f"Error updating row: {e}")
                return jsonify({"error": str(e)}), 500

        @self._blueprint.route("/tables/<table_name>/<row_id>", methods=["DELETE"])
        @admin_required
        def delete_row(table_name, row_id):
            try:
                self._service.validate_table_name(table_name)
                self._service.delete_row(table_name, row_id)
                return jsonify({"message": "Row deleted successfully."}), 200
            except Exception as e:
                app.logger.error(f"Error deleting row: {e}")
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
