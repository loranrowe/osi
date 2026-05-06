"""Tests for OSI Pydantic models."""
import pytest
from pydantic import ValidationError
from osi.models import AIContext, CustomExtension, Dataset, DialectDef, Field, FieldExpression, DimensionMeta
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


class TestField:
    def test_minimal_valid_field(self):
        field = Field.model_validate({
            "name": "customer_id",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "customer_id"}]
            }
        })
        assert field.name == "customer_id"
        assert field.expression.dialects[0].expression == "customer_id"
        assert field.dimension is None
        assert field.label is None
        assert field.description is None
        assert field.ai_context is None
        assert field.custom_extensions == []

    def test_field_with_dimension(self):
        field = Field.model_validate({
            "name": "order_date",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "order_date"}]
            },
            "dimension": {"is_time": True},
        })
        assert field.dimension is not None
        assert field.dimension.is_time is True

    def test_field_with_ai_context_string(self):
        field = Field.model_validate({
            "name": "revenue",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "amount"}]
            },
            "ai_context": "revenue field for reporting",
        })
        assert field.ai_context is not None
        assert field.ai_context.instructions == "revenue field for reporting"

    def test_field_with_ai_context_dict(self):
        field = Field.model_validate({
            "name": "revenue",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "amount"}]
            },
            "ai_context": {
                "synonyms": ["income", "sales"],
            },
        })
        assert field.ai_context.synonyms == ["income", "sales"]

    def test_field_missing_name(self):
        with pytest.raises(ValidationError):
            Field.model_validate({
                "expression": {
                    "dialects": [{"dialect": "ANSI_SQL", "expression": "col"}]
                }
            })

    def test_field_missing_expression(self):
        with pytest.raises(ValidationError):
            Field.model_validate({"name": "test"})

    def test_field_extra_fields_rejected(self):
        with pytest.raises(ValidationError):
            Field.model_validate({
                "name": "test",
                "expression": {
                    "dialects": [{"dialect": "ANSI_SQL", "expression": "col"}]
                },
                "unkown_fild": 42,
            })


class TestDataset:
    def test_minimal_valid_dataset(self):
        ds = Dataset.model_validate({"name": "orders", "source": "sales.public.orders"})
        assert ds.name == "orders"; assert ds.source == "sales.public.orders"
        assert ds.primary_key == []; assert ds.unique_keys == []; assert ds.fields == []

    def test_dataset_with_primary_key(self):
        ds = Dataset.model_validate({"name": "orders", "source": "sales.orders", "primary_key": ["order_id"]})
        assert ds.primary_key == ["order_id"]

    def test_dataset_with_composite_primary_key(self):
        ds = Dataset.model_validate({"name": "order_lines", "source": "sales.order_lines", "primary_key": ["order_id", "line_number"]})
        assert ds.primary_key == ["order_id", "line_number"]

    def test_dataset_with_unique_keys(self):
        ds = Dataset.model_validate({"name": "customers", "source": "sales.customers", "unique_keys": [["email"], ["first_name", "last_name"]]})
        assert ds.unique_keys == [["email"], ["first_name", "last_name"]]

    def test_dataset_with_fields(self):
        ds = Dataset.model_validate({"name": "orders", "source": "sales.orders", "fields": [{"name": "order_id", "expression": {"dialects": [{"dialect": "ANSI_SQL", "expression": "order_id"}]}}]})
        assert len(ds.fields) == 1; assert ds.fields[0].name == "order_id"

    def test_dataset_missing_name(self):
        with pytest.raises(ValidationError): Dataset.model_validate({"source": "sales.orders"})

    def test_dataset_missing_source(self):
        with pytest.raises(ValidationError): Dataset.model_validate({"name": "orders"})
