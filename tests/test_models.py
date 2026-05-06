"""Tests for OSI Pydantic models."""
import pytest
from pydantic import ValidationError
from osi.models import AIContext, CustomExtension, DialectDef, FieldExpression, DimensionMeta
from osi.enums import Dialect, Vendor


class TestDialectDef:
    def test_minimal_valid(self):
        d = DialectDef.model_validate({"dialect": "ANSI_SQL", "expression": "customer_id"})
        assert d.dialect == Dialect.ANSI_SQL
        assert d.expression == "customer_id"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            DialectDef.model_validate({})
        with pytest.raises(ValidationError):
            DialectDef.model_validate({"dialect": "ANSI_SQL"})
        with pytest.raises(ValidationError):
            DialectDef.model_validate({"expression": "col"})

    def test_invalid_dialect(self):
        with pytest.raises(ValidationError):
            DialectDef.model_validate({"dialect": "NOT_REAL", "expression": "col"})

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            DialectDef.model_validate({"dialect": "ANSI_SQL", "expression": "col", "typo_fild": 1})


class TestFieldExpression:
    def test_minimal_valid(self):
        fe = FieldExpression.model_validate({
            "dialects": [{"dialect": "ANSI_SQL", "expression": "col"}]
        })
        assert len(fe.dialects) == 1

    def test_multiple_dialects(self):
        fe = FieldExpression.model_validate({
            "dialects": [
                {"dialect": "ANSI_SQL", "expression": "LOWER(email)"},
                {"dialect": "SNOWFLAKE", "expression": "LOWER(email)::VARCHAR"},
            ]
        })
        assert len(fe.dialects) == 2
        assert fe.dialects[0].dialect == Dialect.ANSI_SQL
        assert fe.dialects[1].dialect == Dialect.SNOWFLAKE

    def test_empty_dialects_allowed(self):
        fe = FieldExpression.model_validate({"dialects": []})
        assert fe.dialects == []


class TestDimensionMeta:
    def test_default_values(self):
        dm = DimensionMeta.model_validate({})
        assert dm.is_time is False

    def test_is_time_true(self):
        dm = DimensionMeta.model_validate({"is_time": True})
        assert dm.is_time is True

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            DimensionMeta.model_validate({"is_time": True, "unknown": 1})


class TestAIContext:
    def test_from_structured_dict(self):
        ctx = AIContext.model_validate({
            "instructions": "Use this for sales analysis",
            "synonyms": ["orders", "purchases"],
            "examples": ["Show total sales last month"],
        })
        assert ctx.instructions == "Use this for sales analysis"
        assert ctx.synonyms == ["orders", "purchases"]
        assert ctx.examples == ["Show total sales last month"]

    def test_from_plain_string(self):
        ctx = AIContext.model_validate("use this for sales")
        assert ctx.instructions == "use this for sales"
        assert ctx.synonyms == []
        assert ctx.examples == []

    def test_default_values(self):
        ctx = AIContext.model_validate({})
        assert ctx.instructions is None
        assert ctx.synonyms == []
        assert ctx.examples == []

    def test_none_input(self):
        ctx = AIContext.model_validate(None)
        assert ctx.instructions is None


class TestCustomExtension:
    def test_valid_extension(self):
        ext = CustomExtension.model_validate({
            "vendor_name": "DBT",
            "data": '{"project_name": "analytics"}'
        })
        assert ext.vendor_name == Vendor.DBT
        assert ext.data == '{"project_name": "analytics"}'

    def test_invalid_vendor(self):
        with pytest.raises(ValidationError):
            CustomExtension.model_validate({"vendor_name": "UNKNOWN", "data": "{}"})

    def test_missing_data(self):
        with pytest.raises(ValidationError):
            CustomExtension.model_validate({"vendor_name": "SNOWFLAKE"})
