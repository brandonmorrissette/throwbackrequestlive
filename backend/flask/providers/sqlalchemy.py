"""
This module provides a custom JSON provider for Flask that handles
serialization of SQLAlchemy objects.
"""

import logging
import types
from collections.abc import Iterable, Mapping
from datetime import datetime

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

from backend.flask.providers.json import JSONProvider


class SQLALchemyJSONProvider(JSONProvider):
    """
    Custom JSON provider for Flask that extends the default JSON provider.

    This provider adds support for serializing SQLAlchemy objects.
    """

    def default(self, obj):
        """
        Override the default method to add custom serialization for SQLAlchemy objects.

        Args:
            obj: The object to serialize.

        Returns:
            The serialized object.
        """
        try:
            serialized = None
            match obj:
                case None:
                    return serialized

                case Integer() | String() | Boolean() | Float() | DateTime():
                    logging.debug("SQL Alchemy Primitive encountered: %s", obj)
                    serialized = self._serialize_sqlalchemy_type(obj)

                case Mapping():
                    logging.debug("Dictionary encountered: %s", obj)
                    serialized = {
                        key: self.default(value) for key, value in obj.items()
                    }

                case Constraint():
                    logging.debug("SQLAlchemy Constraint encountered: %s", obj)
                    serialized = self._serialize_constraint(obj)

                case Table():
                    logging.debug("SQLAlchemy Table encountered: %s", obj)
                    serialized = self._serialize_table(obj)

                case Column():
                    logging.debug("SQLAlchemy Column encountered: %s", obj)
                    serialized = self._serialize_column(obj)

                case str() | int() | float() | bool() | bytes():
                    logging.debug("Primitive encountered: %s", obj)
                    serialized = obj

                case Iterable():
                    logging.debug("Iterable encountered: %s", obj)
                    serialized = [self.default(item) for item in obj]

                case _:
                    logging.debug(
                        "Object of type %s is not serializable", type(obj).__name__
                    )

            return serialized
        except Exception as e:
            logging.error("Error serializing object %s: %s", obj, e)
            raise e

    def _get_attributes(self, obj) -> list:
        """
        Get the attributes of an object that are not callable or methods.

        Args:
            obj: The object to get attributes from.

        Returns:
            A list of attribute names.
        """
        attributes = []
        for attr in dir(obj):
            try:
                if not (attr.startswith("_") or attr.endswith("_")) and not (
                    callable(getattr(obj, attr, None))
                    or isinstance(getattr(obj, attr), types.MethodType)
                ):
                    attributes.append(attr)
            except (AttributeError, TypeError) as e:
                logging.error("Error getting attribute %s: %s", attr, e)
        return attributes

    def _serialize_sqlalchemy_type(self, primitive) -> str:
        """
        Maps SQLAlchemy types to Python types for serialization.

        Args:
            primitive (SQLAlchemy Type): SQLAlchemy column type.

        Returns:
            Python equivalent of the SQLAlchemy type.
        """
        serialized = None
        match primitive:
            case Integer():
                serialized = int.__name__
            case String():
                serialized = str.__name__
            case Boolean():
                serialized = "bool"  # bool does not have a __name__ attribute
            case Float():
                serialized = float.__name__
            case DateTime():
                serialized = datetime.__name__
            case _:
                serialized = str.__name__

        return serialized

    def _serialize_table(
        self,
        table,
        excluded_attributes=None,
    ) -> dict:
        """
        Serialize a SQLAlchemy Table object.

        Args:
            table: The Table object to serialize.
            excluded_attributes: List of attributes to exclude from serialization.
                Default attributes are : c, create_drop_stringify_dialect, dialect_kwargs,
                entity_namespace, dialect_options, dispatch, exported_columns,
                implicit_returning, inherit_cache, is_clause_element, is_selectable,
                kwargs, selectable, stringify_dialect, supports_execution, uses_inspection

        Returns:
            A dictionary of serialized attributes.
        """
        if excluded_attributes is None:
            excluded_attributes = [
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
            ]

        attribute_keys = self._get_attributes(table)
        logging.debug("Table attributes: %s", attribute_keys)
        attributes = {}
        for attribute_key in attribute_keys:
            if attribute_key in excluded_attributes:
                continue

            attribute = getattr(table, attribute_key)
            logging.debug(
                "Serializing Attribute: %s, Value: %s", attribute_key, attribute
            )
            attributes[attribute_key] = self.default(attribute)
        logging.debug("Table %s: %s", table, attributes)
        return attributes

    def _serialize_column(
        self,
        column,
        excluded_attributes=None,
    ) -> dict:
        """
        Serialize a SQLAlchemy Column object.

        Args:
            column: The Column object to serialize.
            excluded_attributes: List of attributes to exclude from serialization.
                Default attributes are : allows_lambda, anon_key_label, anon_label, base_columns,
                bind, comparator, create_drop_stringify_dialect, dialect_kwargs, dialect_options,
                dispatch, entity_namespace, expression, inherit_cache, is_clause_element,
                is_selectable, kwargs, proxy_set, server_default, server_onupdate,
                stringify_dialect, supports_execution, system, table, uses_inspection

        Returns:
            A dictionary of serialized attributes.
        """
        if excluded_attributes is None:
            excluded_attributes = [
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
            ]

        attribute_keys = self._get_attributes(column)
        logging.debug("Column attributes: %s", attribute_keys)
        attributes = {}
        for attr in attribute_keys:
            if attr in excluded_attributes:
                continue
            attribute = getattr(column, attr)
            logging.debug("Serializing Attribute: %s, Value: %s", attr, attribute)
            attributes[attr] = self.default(attribute)
        logging.debug("Column %s: %s", column, attributes)
        return attributes

    def _serialize_constraint(self, constraint):
        """
        Serialize a SQLAlchemy Constraint object.

        Args:
            constraint: The Constraint object to serialize.

        Returns:
            A serialized representation of the constraint.
        """
        if isinstance(constraint, PrimaryKeyConstraint):
            logging.debug("PrimaryKey: %s", constraint)
            return self.default(constraint.columns)

        if isinstance(constraint, ForeignKeyConstraint):
            references = [
                f"{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}"
                for fk in constraint.elements
            ]
            foreign_key = f"ForeignKey({', '.join(references)})"
            logging.debug("ForeignKey: %s", foreign_key)
            return foreign_key

        if isinstance(constraint, UniqueConstraint):
            unique_constraint = (
                f"UniqueConstraint({', '.join(col.name for col in constraint.columns)})"
            )
            logging.debug("UniqueConstraint: %s", unique_constraint)
            return unique_constraint

        columns = getattr(constraint, "columns", [])
        column_names = ", ".join(col.name for col in columns)
        constraint = f"Constraint({column_names})"
        logging.debug("Constraint: %s", constraint)
        return constraint
