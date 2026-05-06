# OSI Minimal Parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Python library that parses OSI v0.1.1 YAML/JSON semantic models into typed Pydantic objects with validation.

**Architecture:** 5 source files — `enums.py` (Dialect/Vendor), `exceptions.py` (error hierarchy), `models.py` (11 Pydantic models with validation), `parser.py` (YAML/JSON loader), `__init__.py` (public API). TDD: each component has tests written before implementation.

**Tech Stack:** Python >=3.11, Pydantic >=2.0, PyYAML >=6.0, pytest >=8.0, mypy >=1.0

---

### Task 1: Project scaffolding

**Files:**
- Create: `E:\project\guide\osi\pyproject.toml`
- Create: `E:\project\guide\osi\osi\__init__.py` (empty placeholder)
- Create: `E:\project\guide\osi\tests\__init__.py` (empty)

- [ ] **Step 1: Create pyproject.toml**

Write `E:\project\guide\osi\pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "osi-parser"
version = "0.1.0"
description = "Minimal OSI (Open Semantic Interchange) parser for AI agents"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "mypy>=1.0",
]

[tool.setuptools]
py-modules = []
```

- [ ] **Step 2: Create empty package files**

Run: `mkdir -p "E:/project/guide/osi/osi" && mkdir -p "E:/project/guide/osi/tests"`

Write `E:\project\guide\osi\osi\__init__.py`: (empty file)

Write `E:\project\guide\osi\tests\__init__.py`: (empty file)

- [ ] **Step 3: Install package in dev mode**

Run: `cd "E:/project/guide/osi" && pip install -e ".[dev]"`

- [ ] **Step 4: Verify import works**

Run: `python -c "import osi; print('OK')"`

Expected: `OK`

---

### Task 2: Enums and Exceptions (TDD)

**Files:**
- Create: `E:\project\guide\osi\osi\enums.py`
- Create: `E:\project\guide\osi\osi\exceptions.py`
- Create: `E:\project\guide\osi\tests\test_enums.py`
- Create: `E:\project\guide\osi\tests\test_exceptions.py`

- [ ] **Step 1: Write failing test for enums**

Write `E:\project\guide\osi\tests\test_enums.py`:

```python
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
```

- [ ] **Step 2: Write failing test for exceptions**

Write `E:\project\guide\osi\tests\test_exceptions.py`:

```python
"""Tests for OSI custom exceptions."""
import pytest
from osi.exceptions import OsiError, OsiValidationError, OsiIntegrityError


def test_osi_error_is_base():
    assert issubclass(OsiValidationError, OsiError)
    assert issubclass(OsiIntegrityError, OsiError)


def test_osi_validation_error_contains_message():
    err = OsiValidationError("数据集 'orders' 缺少必填字段 source")
    assert "orders" in str(err)
    assert "source" in str(err)


def test_osi_integrity_error_contains_message():
    err = OsiIntegrityError("关系 'r1' 引用的目标数据集 'x' 不存在")
    assert "r1" in str(err)
    assert "x" in str(err)


def test_osi_error_raises_normally():
    with pytest.raises(OsiError):
        raise OsiValidationError("test")


def test_error_is_exception():
    assert issubclass(OsiError, Exception)
```

- [ ] **Step 3: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_enums.py tests/test_exceptions.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'osi.enums'`

- [ ] **Step 4: Implement enums.py**

Write `E:\project\guide\osi\osi\enums.py`:

```python
"""OSI enumerations: Dialect and Vendor."""
from enum import Enum


class Dialect(str, Enum):
    ANSI_SQL = "ANSI_SQL"
    SNOWFLAKE = "SNOWFLAKE"
    MDX = "MDX"
    TABLEAU = "TABLEAU"
    DATABRICKS = "DATABRICKS"


class Vendor(str, Enum):
    COMMON = "COMMON"
    SNOWFLAKE = "SNOWFLAKE"
    SALESFORCE = "SALESFORCE"
    DBT = "DBT"
    DATABRICKS = "DATABRICKS"
```

- [ ] **Step 5: Implement exceptions.py**

Write `E:\project\guide\osi\osi\exceptions.py`:

```python
"""OSI custom exceptions for agent-readable errors."""


class OsiError(Exception):
    """Base exception for all OSI errors."""
    pass


class OsiValidationError(OsiError):
    """Validation failure — wraps Pydantic ValidationError with readable paths."""
    pass


class OsiIntegrityError(OsiError):
    """Referential integrity violation — e.g., relationship references unknown dataset."""
    pass
```

- [ ] **Step 6: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_enums.py tests/test_exceptions.py -v`

Expected: 8 passed

---

### Task 3: Leaf models — DialectDef, FieldExpression, DimensionMeta (TDD)

**Files:**
- Create: `E:\project\guide\osi\osi\models.py`
- Create: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Write failing tests for leaf models**

Write `E:\project\guide\osi\tests\test_models.py`:

```python
"""Tests for OSI Pydantic models."""
import pytest
from pydantic import ValidationError
from osi.models import DialectDef, FieldExpression, DimensionMeta, AIContext
from osi.enums import Dialect


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
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'osi.models'`

- [ ] **Step 3: Implement leaf models**

Write `E:\project\guide\osi\osi\models.py`:

```python
"""OSI Pydantic models — typed representations of OSI semantic model entities."""
from pydantic import BaseModel

from .enums import Dialect, Vendor


class DialectDef(BaseModel):
    model_config = {"extra": "forbid"}
    dialect: Dialect
    expression: str


class FieldExpression(BaseModel):
    model_config = {"extra": "forbid"}
    dialects: list[DialectDef]


class DimensionMeta(BaseModel):
    model_config = {"extra": "forbid"}
    is_time: bool = False
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v`

Expected: 7 passed

---

### Task 4: AIContext and CustomExtension (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for AIContext and CustomExtension**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "AIContext or CustomExtension"`

Expected: FAIL — `NameError: name 'AIContext' is not defined`

- [ ] **Step 3: Implement AIContext and CustomExtension**

Append to `E:\project\guide\osi\osi\models.py`:

```python
from pydantic import BaseModel, field_validator


class AIContext(BaseModel):
    model_config = {"extra": "forbid"}
    instructions: str | None = None
    synonyms: list[str] = []
    examples: list[str] = []

    @field_validator("synonyms", "examples", mode="before")
    @classmethod
    def _default_empty_list(cls, v):
        return v or []

    @field_validator("instructions", mode="before")
    @classmethod
    def _wrap_string(cls, v):
        """Accept bare string input and treat it as instructions."""
        if isinstance(v, str) and not isinstance(v, dict):
            return v
        return v


class CustomExtension(BaseModel):
    model_config = {"extra": "forbid"}
    vendor_name: Vendor
    data: str
```

Note: the `AIContext` string coercion is handled by a Pydantic `__init__` workaround — when `model_validate` receives a plain string, we need an `__init__` override or a `@model_validator(mode='wrap')`. Replace Step 3 with this correct implementation:

```python
from pydantic import BaseModel, field_validator, model_validator


class AIContext(BaseModel):
    model_config = {"extra": "forbid"}
    instructions: str | None = None
    synonyms: list[str] = []
    examples: list[str] = []

    @field_validator("synonyms", "examples", mode="before")
    @classmethod
    def _default_empty_list(cls, v):
        return v or []

    @model_validator(mode="wrap")
    @classmethod
    def _wrap_string(cls, data, handler):
        if isinstance(data, str):
            data = {"instructions": data}
        return handler(data)


class CustomExtension(BaseModel):
    model_config = {"extra": "forbid"}
    vendor_name: Vendor
    data: str
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "AIContext or CustomExtension"`

Expected: 7 passed

---

### Task 5: Field model (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for Field**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestField"`

Expected: FAIL — `NameError: name 'Field' is not defined`

- [ ] **Step 3: Implement Field model**

Append to `E:\project\guide\osi\osi\models.py`:

```python
class Field(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    expression: FieldExpression
    dimension: DimensionMeta | None = None
    label: str | None = None
    description: str | None = None
    ai_context: AIContext | str | None = None
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestField"`

Expected: 7 passed

---

### Task 6: Dataset model (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for Dataset**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
class TestDataset:
    def test_minimal_valid_dataset(self):
        ds = Dataset.model_validate({
            "name": "orders",
            "source": "sales.public.orders",
        })
        assert ds.name == "orders"
        assert ds.source == "sales.public.orders"
        assert ds.primary_key == []
        assert ds.unique_keys == []
        assert ds.fields == []

    def test_dataset_with_primary_key(self):
        ds = Dataset.model_validate({
            "name": "orders",
            "source": "sales.orders",
            "primary_key": ["order_id"],
        })
        assert ds.primary_key == ["order_id"]

    def test_dataset_with_composite_primary_key(self):
        ds = Dataset.model_validate({
            "name": "order_lines",
            "source": "sales.order_lines",
            "primary_key": ["order_id", "line_number"],
        })
        assert ds.primary_key == ["order_id", "line_number"]

    def test_dataset_with_unique_keys(self):
        ds = Dataset.model_validate({
            "name": "customers",
            "source": "sales.customers",
            "unique_keys": [["email"], ["first_name", "last_name"]],
        })
        assert ds.unique_keys == [["email"], ["first_name", "last_name"]]

    def test_dataset_with_fields(self):
        ds = Dataset.model_validate({
            "name": "orders",
            "source": "sales.orders",
            "fields": [
                {
                    "name": "order_id",
                    "expression": {
                        "dialects": [{"dialect": "ANSI_SQL", "expression": "order_id"}]
                    }
                }
            ],
        })
        assert len(ds.fields) == 1
        assert ds.fields[0].name == "order_id"

    def test_dataset_missing_name(self):
        with pytest.raises(ValidationError):
            Dataset.model_validate({"source": "sales.orders"})

    def test_dataset_missing_source(self):
        with pytest.raises(ValidationError):
            Dataset.model_validate({"name": "orders"})
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestDataset"`

Expected: FAIL — `NameError: name 'Dataset' is not defined`

- [ ] **Step 3: Implement Dataset model**

Append to `E:\project\guide\osi\osi\models.py`:

```python
class Dataset(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    source: str
    primary_key: list[str] = []
    unique_keys: list[list[str]] = []
    description: str | None = None
    ai_context: AIContext | str | None = None
    fields: list[Field] = []
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestDataset"`

Expected: 7 passed

---

### Task 7: Relationship model (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for Relationship**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
class TestRelationship:
    def test_minimal_valid_relationship(self):
        rel = Relationship.model_validate({
            "name": "orders_to_customers",
            "from": "orders",
            "to": "customers",
            "from_columns": ["customer_id"],
            "to_columns": ["id"],
        })
        assert rel.name == "orders_to_customers"
        assert rel.from_ == "orders"
        assert rel.to == "customers"
        assert rel.from_columns == ["customer_id"]
        assert rel.to_columns == ["id"]

    def test_composite_relationship(self):
        rel = Relationship.model_validate({
            "name": "order_lines_to_products",
            "from": "order_lines",
            "to": "products",
            "from_columns": ["product_id", "variant_id"],
            "to_columns": ["id", "variant_id"],
        })
        assert len(rel.from_columns) == 2
        assert len(rel.to_columns) == 2

    def test_column_count_mismatch_raises(self):
        with pytest.raises(ValidationError):
            Relationship.model_validate({
                "name": "bad_rel",
                "from": "orders",
                "to": "customers",
                "from_columns": ["col1", "col2"],
                "to_columns": ["col1"],
            })

    def test_missing_from_columns(self):
        with pytest.raises(ValidationError):
            Relationship.model_validate({
                "name": "rel",
                "from": "a",
                "to": "b",
                "to_columns": ["col1"],
            })

    def test_relationship_ai_context(self):
        rel = Relationship.model_validate({
            "name": "r1",
            "from": "orders",
            "to": "customers",
            "from_columns": ["x"],
            "to_columns": ["y"],
            "ai_context": "joins order to customer",
        })
        assert rel.ai_context.instructions == "joins order to customer"
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestRelationship"`

Expected: FAIL — `NameError: name 'Relationship' is not defined`

- [ ] **Step 3: Implement Relationship model**

Append to `E:\project\guide\osi\osi\models.py`:

```python
from pydantic import BaseModel, Field as PydanticField, field_validator, model_validator


class Relationship(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    from_: str = PydanticField(alias="from")
    to: str
    from_columns: list[str]
    to_columns: list[str]
    ai_context: AIContext | str | None = None
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v

    @model_validator(mode="after")
    def _check_column_count(self):
        if len(self.from_columns) != len(self.to_columns):
            raise ValueError(
                f"from_columns and to_columns must have same length, "
                f"got {len(self.from_columns)} and {len(self.to_columns)}"
            )
        return self
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestRelationship"`

Expected: 5 passed

---

### Task 8: Metric model (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for Metric**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
class TestMetric:
    def test_minimal_valid_metric(self):
        m = Metric.model_validate({
            "name": "total_revenue",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "SUM(orders.amount)"}]
            }
        })
        assert m.name == "total_revenue"
        assert m.expression.dialects[0].expression == "SUM(orders.amount)"

    def test_metric_with_description_and_synonyms(self):
        m = Metric.model_validate({
            "name": "total_revenue",
            "expression": {
                "dialects": [{"dialect": "ANSI_SQL", "expression": "SUM(orders.amount)"}]
            },
            "description": "Total revenue across all orders",
            "ai_context": {
                "synonyms": ["total sales", "revenue"],
            },
        })
        assert m.description == "Total revenue across all orders"
        assert m.ai_context.synonyms == ["total sales", "revenue"]

    def test_metric_missing_name(self):
        with pytest.raises(ValidationError):
            Metric.model_validate({
                "expression": {
                    "dialects": [{"dialect": "ANSI_SQL", "expression": "SUM(x)"}]
                }
            })

    def test_metric_missing_expression(self):
        with pytest.raises(ValidationError):
            Metric.model_validate({"name": "test_metric"})
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestMetric"`

Expected: FAIL — `NameError: name 'Metric' is not defined`

- [ ] **Step 3: Implement Metric model**

Append to `E:\project\guide\osi\osi\models.py`:

```python
class Metric(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    expression: FieldExpression
    description: str | None = None
    ai_context: AIContext | str | None = None
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestMetric"`

Expected: 4 passed

---

### Task 9: SemanticModel and OSIDocument (TDD)

**Files:**
- Modify: `E:\project\guide\osi\osi\models.py`
- Modify: `E:\project\guide\osi\tests\test_models.py`

- [ ] **Step 1: Add failing tests for SemanticModel and OSIDocument**

Append to `E:\project\guide\osi\tests\test_models.py`:

```python
class TestSemanticModel:
    def test_minimal_valid_model(self):
        sm = SemanticModel.model_validate({
            "name": "sales_analytics",
            "datasets": [
                {"name": "orders", "source": "sales.orders"},
            ],
        })
        assert sm.name == "sales_analytics"
        assert len(sm.datasets) == 1
        assert sm.relationships == []
        assert sm.metrics == []

    def test_full_model(self):
        sm = SemanticModel.model_validate({
            "name": "ecommerce",
            "description": "E-commerce analytics",
            "ai_context": "use for sales analysis",
            "datasets": [
                {
                    "name": "orders",
                    "source": "sales.orders",
                    "fields": [
                        {
                            "name": "order_id",
                            "expression": {
                                "dialects": [{"dialect": "ANSI_SQL", "expression": "order_id"}]
                            }
                        }
                    ]
                },
                {
                    "name": "customers",
                    "source": "sales.customers",
                    "fields": [
                        {
                            "name": "id",
                            "expression": {
                                "dialects": [{"dialect": "ANSI_SQL", "expression": "id"}]
                            }
                        }
                    ]
                },
            ],
            "relationships": [
                {
                    "name": "orders_to_customers",
                    "from": "orders",
                    "to": "customers",
                    "from_columns": ["customer_id"],
                    "to_columns": ["id"],
                }
            ],
            "metrics": [
                {
                    "name": "total_revenue",
                    "expression": {
                        "dialects": [{"dialect": "ANSI_SQL", "expression": "SUM(orders.amount)"}]
                    }
                }
            ],
        })
        assert len(sm.relationships) == 1
        assert len(sm.metrics) == 1

    def test_referential_integrity_bad_from(self):
        with pytest.raises(ValidationError):
            SemanticModel.model_validate({
                "name": "test",
                "datasets": [{"name": "orders", "source": "sales.orders"}],
                "relationships": [
                    {
                        "name": "bad",
                        "from": "nonexistent",
                        "to": "orders",
                        "from_columns": ["x"],
                        "to_columns": ["y"],
                    }
                ],
            })

    def test_referential_integrity_bad_to(self):
        with pytest.raises(ValidationError):
            SemanticModel.model_validate({
                "name": "test",
                "datasets": [{"name": "orders", "source": "sales.orders"}],
                "relationships": [
                    {
                        "name": "bad",
                        "from": "orders",
                        "to": "nonexistent",
                        "from_columns": ["x"],
                        "to_columns": ["y"],
                    }
                ],
            })

    def test_missing_datasets(self):
        with pytest.raises(ValidationError):
            SemanticModel.model_validate({"name": "test"})

    def test_with_custom_extensions(self):
        sm = SemanticModel.model_validate({
            "name": "test",
            "datasets": [{"name": "orders", "source": "sales.orders"}],
            "custom_extensions": [
                {"vendor_name": "SNOWFLAKE", "data": '{"warehouse": "ANALYTICS_WH"}'}
            ],
        })
        assert len(sm.custom_extensions) == 1
        assert sm.custom_extensions[0].vendor_name == "SNOWFLAKE"


class TestOSIDocument:
    def test_wraps_models(self):
        sm = SemanticModel.model_validate({
            "name": "test",
            "datasets": [{"name": "orders", "source": "sales.orders"}],
        })
        doc = OSIDocument(models=[sm])
        assert len(doc.models) == 1
        assert doc.models[0].name == "test"

    def test_empty_models(self):
        doc = OSIDocument(models=[])
        assert doc.models == []
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestSemanticModel or TestOSIDocument"`

Expected: FAIL — `NameError: name 'SemanticModel' is not defined`

- [ ] **Step 3: Implement SemanticModel and OSIDocument**

Append to `E:\project\guide\osi\osi\models.py`:

```python
class SemanticModel(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    description: str | None = None
    ai_context: AIContext | str | None = None
    datasets: list[Dataset]
    relationships: list[Relationship] = []
    metrics: list[Metric] = []
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v

    @model_validator(mode="after")
    def _check_referential_integrity(self):
        dataset_names = {d.name for d in self.datasets}
        for rel in self.relationships:
            if rel.from_ not in dataset_names:
                raise ValueError(
                    f"Relationship '{rel.name}': 'from' dataset '{rel.from_}' "
                    f"not found in datasets"
                )
            if rel.to not in dataset_names:
                raise ValueError(
                    f"Relationship '{rel.name}': 'to' dataset '{rel.to}' "
                    f"not found in datasets"
                )
        return self


class OSIDocument(BaseModel):
    model_config = {"extra": "forbid"}
    models: list[SemanticModel]
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v -k "TestSemanticModel or TestOSIDocument"`

Expected: 8 passed

---

### Task 10: Run all model tests

- [ ] **Step 1: Run full test suite for models**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_models.py -v`

Expected: 38 passed

---

### Task 11: Parser — load_osi function (TDD)

**Files:**
- Create: `E:\project\guide\osi\osi\parser.py`
- Create: `E:\project\guide\osi\tests\test_parser.py`

- [ ] **Step 1: Create test fixture YAML**

Write `E:\project\guide\osi\tests\fixtures\valid_minimal.yaml`:

```yaml
semantic_model:
  - name: test_model
    description: A minimal test model
    datasets:
      - name: orders
        source: sales.orders
```

- [ ] **Step 2: Write failing tests for parser**

Write `E:\project\guide\osi\tests\test_parser.py`:

```python
"""Tests for OSI parser — YAML/JSON loading."""
from pathlib import Path
import pytest
from osi.parser import load_osi
from osi.exceptions import OsiValidationError


FIXTURES = Path(__file__).parent / "fixtures"


def test_load_minimal_yaml():
    doc = load_osi(FIXTURES / "valid_minimal.yaml")
    assert len(doc.models) == 1
    assert doc.models[0].name == "test_model"
    assert doc.models[0].datasets[0].name == "orders"


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_osi(FIXTURES / "nonexistent.yaml")


def test_load_invalid_yaml():
    with pytest.raises((OsiValidationError, Exception)):
        load_osi(FIXTURES / "invalid_schema.yaml")
```

- [ ] **Step 3: Create invalid fixture**

Write `E:\project\guide\osi\tests\fixtures\invalid_schema.yaml`:

```yaml
semantic_model:
  - name: bad_model
    # missing required 'datasets' field
```

- [ ] **Step 4: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_parser.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'osi.parser'`

- [ ] **Step 5: Implement parser**

Write `E:\project\guide\osi\osi\parser.py`:

```python
"""OSI model loader — YAML/JSON → Pydantic objects."""
from pathlib import Path
import json

import yaml
from pydantic import ValidationError

from .models import OSIDocument, SemanticModel
from .exceptions import OsiValidationError


def load_osi(path: str | Path) -> OSIDocument:
    path = Path(path)
    text = path.read_text(encoding="utf-8")

    if path.suffix in (".yaml", ".yml"):
        raw = yaml.safe_load(text)
    elif path.suffix == ".json":
        raw = json.loads(text)
    else:
        raise OsiValidationError(f"Unsupported file format: {path.suffix}")

    if isinstance(raw, dict) and "semantic_model" in raw:
        model_list = raw["semantic_model"]
    else:
        model_list = raw

    if not isinstance(model_list, list):
        model_list = [model_list]

    try:
        models = [SemanticModel.model_validate(m) for m in model_list]
    except ValidationError as e:
        raise OsiValidationError(str(e)) from e

    return OSIDocument(models=models)
```

- [ ] **Step 6: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_parser.py -v`

Expected: 3 passed

---

### Task 12: __init__.py — Public API

**Files:**
- Modify: `E:\project\guide\osi\osi\__init__.py`

- [ ] **Step 1: Write failing import test**

Create `E:\project\guide\osi\tests\test_public_api.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_public_api.py -v`

Expected: FAIL — some attributes missing

- [ ] **Step 3: Implement __init__.py**

Write `E:\project\guide\osi\osi\__init__.py`:

```python
"""OSI Minimal Parser — typed semantic model loading for AI agents."""
from .enums import Dialect, Vendor
from .exceptions import OsiError, OsiValidationError, OsiIntegrityError
from .models import (
    AIContext,
    CustomExtension,
    DialectDef,
    DimensionMeta,
    FieldExpression,
    Field,
    Dataset,
    Relationship,
    Metric,
    SemanticModel,
    OSIDocument,
)
from .parser import load_osi

__all__ = [
    "load_osi",
    "OSIDocument",
    "SemanticModel",
    "Dataset",
    "Field",
    "Metric",
    "Relationship",
    "AIContext",
    "CustomExtension",
    "FieldExpression",
    "DialectDef",
    "DimensionMeta",
    "Dialect",
    "Vendor",
    "OsiError",
    "OsiValidationError",
    "OsiIntegrityError",
]
```

- [ ] **Step 4: Run tests to confirm pass**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_public_api.py -v`

Expected: 4 passed

---

### Task 13: Integration test — full OSI model round-trip

**Files:**
- Create: `E:\project\guide\osi\tests\fixtures\ecommerce_full.yaml`
- Create: `E:\project\guide\osi\tests\test_integration.py`

- [ ] **Step 1: Create ecommerce fixture from spec example**

Write `E:\project\guide\osi\tests\fixtures\ecommerce_full.yaml`:

```yaml
semantic_model:
  - name: ecommerce_analytics
    description: E-commerce sales and customer analytics
    ai_context:
      instructions: Use this model for analyzing sales trends, customer behavior, and product performance
    datasets:
      - name: orders
        source: sales.public.orders
        primary_key: [order_id]
        description: Customer orders
        fields:
          - name: order_id
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: order_id
            description: Order identifier
          - name: customer_id
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: customer_id
            description: Customer identifier
          - name: order_date
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: order_date
            dimension:
              is_time: true
            description: Order date
          - name: amount
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: amount
            description: Order amount
      - name: customers
        source: sales.public.customers
        primary_key: [id]
        description: Customer information
        fields:
          - name: id
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: id
            description: Customer identifier
          - name: email
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: email
            description: Customer email
    relationships:
      - name: orders_to_customers
        from: orders
        to: customers
        from_columns: [customer_id]
        to_columns: [id]
    metrics:
      - name: total_revenue
        expression:
          dialects:
            - dialect: ANSI_SQL
              expression: SUM(orders.amount)
        description: Total revenue from all orders
        ai_context:
          synonyms:
            - total sales
            - revenue
      - name: customer_count
        expression:
          dialects:
            - dialect: ANSI_SQL
              expression: COUNT(DISTINCT customers.id)
        description: Total number of customers
        ai_context:
          synonyms:
            - total customers
            - customer base
    custom_extensions:
      - vendor_name: SNOWFLAKE
        data: '{"warehouse": "ANALYTICS_WH"}'
```

- [ ] **Step 2: Write integration tests**

Write `E:\project\guide\osi\tests\test_integration.py`:

```python
"""Integration tests — full OSI model round-trip."""
from pathlib import Path
from osi import load_osi

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_ecommerce_full():
    doc = load_osi(FIXTURES / "ecommerce_full.yaml")
    model = doc.models[0]

    assert model.name == "ecommerce_analytics"
    assert len(model.datasets) == 2
    assert len(model.relationships) == 1
    assert len(model.metrics) == 2
    assert len(model.custom_extensions) == 1


def test_dataset_structure():
    doc = load_osi(FIXTURES / "ecommerce_full.yaml")
    orders = doc.models[0].datasets[0]

    assert orders.name == "orders"
    assert orders.source == "sales.public.orders"
    assert orders.primary_key == ["order_id"]
    assert len(orders.fields) == 4

    time_field = orders.fields[2]
    assert time_field.name == "order_date"
    assert time_field.dimension is not None
    assert time_field.dimension.is_time is True


def test_relationship_structure():
    doc = load_osi(FIXTURES / "ecommerce_full.yaml")
    rel = doc.models[0].relationships[0]

    assert rel.name == "orders_to_customers"
    assert rel.from_ == "orders"
    assert rel.to == "customers"
    assert rel.from_columns == ["customer_id"]
    assert rel.to_columns == ["id"]


def test_metric_structure():
    doc = load_osi(FIXTURES / "ecommerce_full.yaml")
    total_rev = doc.models[0].metrics[0]

    assert total_rev.name == "total_revenue"
    assert total_rev.ai_context.synonyms == ["total sales", "revenue"]
    assert total_rev.description == "Total revenue from all orders"


def test_ai_context_parsed():
    doc = load_osi(FIXTURES / "ecommerce_full.yaml")
    model = doc.models[0]

    assert model.ai_context is not None
    assert "sales trends" in model.ai_context.instructions
```

- [ ] **Step 3: Run integration tests**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/test_integration.py -v`

Expected: 5 passed

---

### Task 14: Final verification — full suite + type checking

- [ ] **Step 1: Run complete test suite**

Run: `cd "E:/project/guide/osi" && python -m pytest tests/ -v`

Expected: 58 passed (sum of all tests above)

- [ ] **Step 2: Run mypy type checking**

Run: `cd "E:/project/guide/osi" && python -m mypy osi/ --strict`

Expected: 0 errors

- [ ] **Step 3: Verify import from anywhere**

Run: `cd /tmp && python -c "from osi import load_osi, SemanticModel, Dialect; print('OK')"`

Expected: `OK`
