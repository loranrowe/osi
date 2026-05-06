"""Tests for the public API surface."""
import osi


def test_all_exports_present():
    assert hasattr(osi, "load_osi")
    assert hasattr(osi, "OSIDocument")
    assert hasattr(osi, "SemanticModel")
    assert hasattr(osi, "Dataset")
    assert hasattr(osi, "Field")
    assert hasattr(osi, "Metric")
    assert hasattr(osi, "Relationship")
    assert hasattr(osi, "AIContext")
    assert hasattr(osi, "CustomExtension")
    assert hasattr(osi, "FieldExpression")
    assert hasattr(osi, "DialectDef")
    assert hasattr(osi, "DimensionMeta")
    assert hasattr(osi, "Dialect")
    assert hasattr(osi, "Vendor")
    assert hasattr(osi, "OsiError")
    assert hasattr(osi, "OsiValidationError")
    assert hasattr(osi, "OsiIntegrityError")


def test_load_osi_is_callable():
    assert callable(osi.load_osi)


def test_dialect_enum_accessible():
    assert osi.Dialect.ANSI_SQL == "ANSI_SQL"


def test_top_level_imports_work():
    from osi import load_osi, SemanticModel, Dialect
    from osi import OsiError, OsiValidationError
    assert callable(load_osi)
