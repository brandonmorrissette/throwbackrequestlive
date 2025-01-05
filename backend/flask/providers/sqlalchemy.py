import logging
import types
from collections.abc import Iterable, Mapping
from datetime import datetime

from providers.json import JSONProvider
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.schema import Constraint


class SQLALchemyJSONProvider(JSONProvider):
    def default(self, obj):
        try:
            if obj is None:
                return None

            elif isinstance(obj, (Integer, String, Boolean, Float, DateTime)):
                logging.debug(f"SQL Alchemy Primitive encountered: {obj}")
                return self._serialize_sqlalchemy_type(obj)

            elif isinstance(obj, Mapping):
                logging.debug(f"Dictionary encountered: {obj}")
                return {key: self.default(value) for key, value in obj.items()}

            elif isinstance(obj, Constraint):
                logging.debug(f"SQLAlchemy Constraint encountered: {obj}")
                return self._serialize_constraint(obj)

            elif isinstance(obj, Table):
                logging.debug(f"SQLAlchemy Table encountered: {obj}")
                return self._serialize_table(obj)

            elif isinstance(obj, Column):
                logging.debug(f"SQLAlchemy Column encountered: {obj}")
                return self._serialize_column(obj)

            elif isinstance(obj, (str, int, float, bool, bytes)):
                logging.debug(f"Primitive encountered: {obj}")
                return obj

            elif isinstance(obj, Iterable):
                logging.debug(f"Iterable encountered: {obj}")
                return [self.default(item) for item in obj]

            else:
                logging.debug(
                    f"Object of type {type(obj).__name__} is not serializable"
                )
        except Exception as e:
            logging.error(f"Error serializing object {obj}: {e}")
            raise

    def _get_attributes(self, obj):
        attributes = []
        for attr in dir(obj):
            try:
                if not (attr.startswith("_") or attr.endswith("_")) and not (
                    callable(getattr(obj, attr, None))
                    or isinstance(getattr(obj, attr), types.MethodType)
                ):
                    attributes.append(attr)
            except Exception as e:
                logging.error(f"Error getting attribute {attr}: {e}")
        return attributes

    def _serialize_sqlalchemy_type(self, primitive):
        """
        Maps SQLAlchemy types to Python types for serialization.
        Args:
            sa_type (SQLAlchemy Type): SQLAlchemy column type.

        Returns:
            Python equivalent of the SQLAlchemy type.
        """
        if isinstance(primitive, Integer):
            return int.__name__
        elif isinstance(primitive, String):
            return str.__name__
        elif isinstance(primitive, Boolean):
            return "bool"  # bool does not a __name__ attribute, according to the error I ran into
        elif isinstance(primitive, Float):
            return float.__name__
        elif isinstance(primitive, DateTime):
            return datetime.__name__
        else:
            return str.__name__

    def _serialize_table(
        self,
        table,
        excluded_attributes=[
            "c",
            "create_drop_stringify_dialect",
            "dialect_kwargs",
            "entity_namespace",
            "dialect_options",
            "dispatch",
            "exported_columns",
            "implicit_returning",
            "inherit_cache",
            "is_clause_element",
            "is_selectable",
            "kwargs",
            "selectable",
            "stringify_dialect",
            "supports_execution",
            "uses_inspection",
        ],
        # flattened_attributes=["primary_key", "foreign_keys", "indexes"],
    ):
        attribute_keys = self._get_attributes(table)
        logging.debug(f"Table attributes: {attribute_keys}")
        attributes = {}
        for attribute_key in attribute_keys:
            if attribute_key in excluded_attributes:
                continue

            attribute = getattr(table, attribute_key)
            logging.debug(f"Serializing Attribute: {attribute_key}, Value: {attribute}")
            attributes[attribute_key] = self.default(attribute)
        logging.debug(f"Table {table}: {attributes}")
        return attributes

    def _serialize_column(
        self,
        column,
        excluded_attributes=[
            "allows_lambda",
            "anon_key_label",
            "anon_label",
            "base_columns",
            "bind",
            "comparator",
            "create_drop_stringify_dialect",
            "dialect_kwargs",
            "dialect_options",
            "dispatch",
            "entity_namespace",
            "expression",
            "inherit_cache",
            "is_clause_element",
            "is_selectable",
            "kwargs",
            "proxy_set",
            "server_default",
            "server_onupdate",
            "stringify_dialect",
            "supports_execution",
            "system",
            "table",
            "uses_inspection",
        ],
    ):
        attribute_keys = self._get_attributes(column)
        logging.debug(f"Column attributes: {attribute_keys}")
        attributes = {}
        for attr in attribute_keys:
            if attr in excluded_attributes:
                continue
            attribute = getattr(column, attr)
            logging.debug(f"Serializing Attribute: {attr}, Value: {attribute}")
            attributes[attr] = self.default(attribute)
        logging.debug(f"Column {column}: {attributes}")
        return attributes

    def _serialize_constraint(self, constraint):
        if isinstance(constraint, PrimaryKeyConstraint):
            logging.debug(f"PrimaryKey: {constraint}")
            return self.default(constraint.columns)
        elif isinstance(constraint, ForeignKeyConstraint):
            references = [
                f"{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}"
                for fk in constraint.elements
            ]
            foreign_key = f"ForeignKey({', '.join(references)})"
            logging.debug(f"ForeignKey: {foreign_key}")
            return foreign_key
        elif isinstance(constraint, UniqueConstraint):
            unique_constraint = (
                f"Unique({', '.join(col.name for col in constraint.columns)})"
            )
            logging.debug(f"UniqueConstraint: {unique_constraint}")
            return constraint
        else:
            constraint = f"Constraint({', '.join(col.name for col in getattr(constraint, 'columns', []))})"
            logging.debug(f"Constraint: {constraint}")
            return constraint
