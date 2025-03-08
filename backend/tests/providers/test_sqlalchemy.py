# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
from unittest.mock import MagicMock

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.schema import (
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)

from backend.flask.providers.sqlalchemy import SQLALchemyJSONProvider


@pytest.fixture
def app():
    return MagicMock()


@pytest.fixture
def json_provider(app):
    return SQLALchemyJSONProvider(app)


@pytest.fixture
def sample_table():
    metadata = MetaData()
    return Table(
        "sample_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("value", Integer),
        PrimaryKeyConstraint("id"),
        UniqueConstraint("name"),
    )


def test_given_none_when_serializing_then_return_none(json_provider):
    assert json_provider.default(None) is None


def test_given_primitive_when_serializing_then_return_primitive(json_provider):
    assert json_provider.default(123) == 123
    assert json_provider.default("test") == "test"
    assert json_provider.default(True) is True
    assert json_provider.default(123.45) == 123.45


def test_given_mapping_when_serializing_then_return_serialized_mapping(json_provider):
    data = {"key": "value", "number": 123}
    expected = {"key": "value", "number": 123}
    assert json_provider.default(data) == expected


def test_given_table_when_serializing_then_return_serialized_table(
    json_provider, sample_table
):
    serialized = json_provider.default(sample_table)
    assert isinstance(serialized, dict)
    assert "name" in serialized
    assert "columns" in serialized


def test_given_column_when_serializing_then_return_serialized_column(
    json_provider, sample_table
):
    column = sample_table.c.id
    serialized = json_provider.default(column)
    assert isinstance(serialized, dict)
    assert "name" in serialized
    assert serialized["name"] == "id"


def test_given_primary_key_constraint_when_serializing_then_return_serialized_constraint(
    json_provider, sample_table
):
    pk_constraint = sample_table.primary_key
    serialized = json_provider.default(pk_constraint)
    assert isinstance(serialized, list)
    assert any(col["name"] == "id" for col in serialized)


def test_given_foreign_key_constraint_when_serializing_then_return_serialized_constraint(
    json_provider,
):
    metadata = MetaData()
    other_table = Table(
        "other_table",
        metadata,
        Column("id", Integer, primary_key=True),
    )
    sample_table = Table(
        "sample_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        ForeignKeyConstraint(["value"], [other_table.c.id]),
    )
    fk_constraint = next(iter(sample_table.foreign_key_constraints))
    serialized = json_provider.default(fk_constraint)
    assert isinstance(serialized, str)
    assert "ForeignKey(value -> other_table.id)" in serialized


def test_given_unique_constraint_when_serializing_then_return_serialized_constraint(
    json_provider, sample_table
):
    unique_constraint = next(
        constraint
        for constraint in sample_table.constraints
        if isinstance(constraint, UniqueConstraint)
    )
    serialized = json_provider.default(unique_constraint)
    assert isinstance(serialized, str)
    assert "UniqueConstraint(name)" in serialized
