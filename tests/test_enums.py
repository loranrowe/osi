"""Tests for OSI enumerations."""
from osi.enums import Dialect, Vendor


def test_dialect_values():
    assert Dialect.ANSI_SQL.value == "ANSI_SQL"
    assert Dialect.SNOWFLAKE.value == "SNOWFLAKE"
    assert Dialect.MDX.value == "MDX"
    assert Dialect.TABLEAU.value == "TABLEAU"
    assert Dialect.DATABRICKS.value == "DATABRICKS"


def test_dialect_is_string_enum():
    assert Dialect.ANSI_SQL == "ANSI_SQL"
    assert isinstance(Dialect.ANSI_SQL, str)


def test_vendor_values():
    assert Vendor.COMMON.value == "COMMON"
    assert Vendor.SNOWFLAKE.value == "SNOWFLAKE"
    assert Vendor.SALESFORCE.value == "SALESFORCE"
    assert Vendor.DBT.value == "DBT"
    assert Vendor.DATABRICKS.value == "DATABRICKS"


def test_dialect_from_string():
    assert Dialect("ANSI_SQL") == Dialect.ANSI_SQL


def test_vendor_from_string():
    assert Vendor("DBT") == Vendor.DBT
