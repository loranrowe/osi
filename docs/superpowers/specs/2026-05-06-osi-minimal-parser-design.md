# OSI Minimal Parser — Design Spec

**Date:** 2026-05-06
**Version:** 0.1.0
**Status:** draft

## Overview

A minimal Python library that implements the OSI (Open Semantic Interchange) specification v0.1.1 as Pydantic models, providing YAML/JSON parsing with validation. Designed for use by data analysis AI agents that need a typed, validated in-memory representation of OSI semantic models.

## Motivation

OSI v0.1.1 defines a YAML-based specification for semantic models (datasets, fields, relationships, metrics) but has no standard Python implementation. A data analysis agent needs a reliable way to load these models into memory, with type safety and validation, as the foundation for NL2SQL and metrics resolution.

## Design Goals

- **Minimal surface area**: ~300 lines of Python, 5 source files, 2 dependencies
- **Pydantic-native**: Leverage Pydantic v2 for type coercion, required-field validation, and nested model validation — zero hand-written validation boilerplate
- **AI-agent friendly**: Typed objects with IDE-visible fields; clear, readable error messages; one-call loading
- **Strict by default**: Unknown fields rejected (`extra="forbid"`), referential integrity checked
- **One-time load**: Entire model loaded into memory; designed for models in the KB–low MB range

## Package Structure

```
osi/
  __init__.py      # Public API exports
  enums.py         # Dialect, Vendor enumerations (~15 lines)
  models.py        # 11 Pydantic models (~200 lines)
  parser.py        # YAML/JSON → Pydantic loader (~40 lines)
  exceptions.py    # Custom exceptions (~20 lines)
  pyproject.toml   # Project metadata and dependencies
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.0 | Type models, validation, serialization |
| pyyaml | >=6.0 | YAML file reading |
| pytest (dev) | >=8.0 | Testing |
| mypy (dev) | >=1.0 | Static type checking |

Python requirement: >=3.11

## Class Hierarchy

### Enums (`enums.py`)

```
Dialect: ANSI_SQL | SNOWFLAKE | MDX | TABLEAU | DATABRICKS
Vendor:  COMMON | SNOWFLAKE | SALESFORCE | DBT | DATABRICKS
```

### Leaf Models

| Model | Fields | Notes |
|-------|--------|-------|
| `DialectDef` | `dialect: Dialect`, `expression: str` | One expression in one dialect |
| `DimensionMeta` | `is_time: bool = False` | |
| `AIContext` | `instructions: str \| None`, `synonyms: list[str]`, `examples: list[str]` | Accepts `str` on input, auto-converts |
| `CustomExtension` | `vendor_name: Vendor`, `data: str` | JSON string kept as string |

### Core Models

| Model | Required Fields | Optional Fields |
|-------|----------------|-----------------|
| `FieldExpression` | `dialects: list[DialectDef]` | — |
| `Field` | `name: str`, `expression: FieldExpression` | `dimension`, `label`, `description`, `ai_context`, `custom_extensions` |
| `Dataset` | `name: str`, `source: str` | `primary_key`, `unique_keys`, `description`, `ai_context`, `fields`, `custom_extensions` |
| `Relationship` | `name`, `from`, `to`, `from_columns`, `to_columns` | `ai_context`, `custom_extensions` |
| `Metric` | `name: str`, `expression: FieldExpression` | `description`, `ai_context`, `custom_extensions` |

### Top-Level Container

| Model | Fields | Notes |
|-------|--------|-------|
| `SemanticModel` | `name`★, `datasets`★, `description?`, `ai_context?`, `relationships[]`, `metrics[]`, `custom_extensions[]` | Validator checks relationship referential integrity |
| `OSIDocument` | `models: list[SemanticModel]` | Simple wrapper around model list |

## Key Design Decisions

### 1. ai_context dual-type handling
`ai_context` in spec accepts `str | object | None`. On input, a `@field_validator(mode='before')` converts bare strings to `AIContext(instructions=<value>)`. Consumers always get a typed `AIContext` object.

### 2. Metric expression normalization
Spec examples inconsistently show Metric.expression as array or object. Parser normalizes both forms into `FieldExpression(dialects=[...])`.

### 3. custom_extensions.data kept as string
Not auto-parsed. Users call `.parsed_data` property for on-demand JSON parsing. Avoids coupling parser to extension schema.

### 4. Strict mode
All models use `model_config = {"extra": "forbid"}`. Typos in YAML field names produce errors, not silent ignoring.

### 5. Referential integrity
`SemanticModel` has a `@model_validator` that checks every `Relationship.from` and `Relationship.to` references an existing `Dataset.name`.

### 6. Column count alignment
`Relationship` validates `len(from_columns) == len(to_columns)`.

## Public API

```python
from osi import (
    # Loading
    load_osi,              # load_osi(path: str | Path) -> OSIDocument

    # Models
    OSIDocument,
    SemanticModel,
    Dataset, Field, Metric, Relationship,
    AIContext, CustomExtension,
    FieldExpression, DialectDef, DimensionMeta,

    # Enums
    Dialect, Vendor,

    # Exceptions
    OsiError,
    OsiValidationError,    # Wraps Pydantic ValidationError with readable paths
    OsiIntegrityError,     # Referential integrity violations
)
```

## Error Handling

Errors are formatted for agent readability:

```
OsiValidationError: 数据集 'orders' 字段 'order_id': expression 为必填项
OsiIntegrityError: 关系 'orders_to_customers' 引用的目标数据集 'customers' 不存在
```

`OsiValidationError` wraps Pydantic's `ValidationError` and extracts human-readable field paths.

## Out of Scope (MVP)

- JSON Schema validation against osi-schema.json
- SQL dialect-aware expression validation
- Multi-file model composition (Composability WG)
- Sync API client
- Converter to/from vendor formats (dbt, Snowflake, etc.)
- Relationship JOIN path resolution (for SQL generation)

## Future Extensions

When the agent use case demands it, the next increment would add:
- `osi/resolver.py` — resolve metric → SQL using relationship graph traversal
- `osi/tools.py` — LangChain/LlamaIndex tool wrappers exposing model metadata to LLMs
- Vendor converters under `osi/converters/`

## Test Plan

- Unit tests for each Pydantic model (valid/invalid inputs, edge cases)
- Round-trip: parse spec's own examples/TPC-DS YAML
- Validation error message format tests
- `ai_context` string→object coercion
- Metric expression normalization
- Relationship referential integrity
- `extra="forbid"` rejection
- Type checking passes (mypy strict mode)
