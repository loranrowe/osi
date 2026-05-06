# osi-parser

Minimal Python library implementing the [OSI (Open Semantic Interchange)](https://open-semantic-interchange.org/) specification v0.1.1 as typed Pydantic models, with YAML/JSON parsing and validation.

Built for data analysis AI agents that need a reliable way to load semantic models into memory — the foundation for NL2SQL, metric resolution, and semantic query generation.

## Installation

```bash
pip install -e ".[dev]"
```

Requires Python >=3.11.

**Dependencies:** pydantic >=2.0, pyyaml >=6.0  
**Dev:** pytest >=8.0, mypy >=1.0

## Quick Start

```python
from osi import load_osi

# Load a semantic model from YAML
doc = load_osi("ecommerce_model.yaml")

model = doc.models[0]
print(model.name)                              # "ecommerce_analytics"
print(model.metrics[0].name)                   # "total_revenue"
print(model.metrics[0].ai_context.synonyms)    # ["total sales", "revenue"]

# Navigate datasets
orders = model.datasets[0]
print(orders.source)                           # "sales.public.orders"
print(orders.fields[2].dimension.is_time)      # True

# Walk relationships
rel = model.relationships[0]
print(f"{rel.from_} -> {rel.to}")             # "orders -> customers"
```

## Package Structure

```
osi/
  __init__.py      # Public API — 17 exports
  enums.py         # Dialect, Vendor (str Enum)
  exceptions.py    # OsiError, OsiValidationError, OsiIntegrityError
  models.py        # 11 Pydantic models from DialectDef → SemanticModel
  parser.py        # load_osi() — YAML/JSON → OSIDocument
```

## Model Hierarchy

| Model | Description |
|-------|-------------|
| `OSIDocument` | Top-level wrapper containing a list of semantic models |
| `SemanticModel` | Complete model: datasets + relationships + metrics |
| `Dataset` | Logical table with name, source, fields, keys |
| `Field` | Row-level attribute with dialect expressions |
| `Relationship` | Foreign-key join between datasets |
| `Metric` | Aggregate expression spanning one or more datasets |
| `AIContext` | Instructions, synonyms, examples for AI tools |
| `FieldExpression` / `DialectDef` | Multi-dialect SQL expression support |
| `DimensionMeta` | Dimension metadata (e.g., is_time) |
| `CustomExtension` | Vendor-specific metadata blob |

## Public API

```python
from osi import (
    load_osi,              # load_osi(path) -> OSIDocument

    OSIDocument, SemanticModel,
    Dataset, Field, Metric, Relationship,
    AIContext, CustomExtension,
    FieldExpression, DialectDef, DimensionMeta,

    Dialect, Vendor,

    OsiError, OsiValidationError, OsiIntegrityError,
)
```

## Example OSI Model (YAML)

```yaml
semantic_model:
  - name: ecommerce_analytics
    datasets:
      - name: orders
        source: sales.public.orders
        primary_key: [order_id]
        fields:
          - name: amount
            expression:
              dialects:
                - dialect: ANSI_SQL
                  expression: amount
      - name: customers
        source: sales.public.customers
        primary_key: [id]
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
        ai_context:
          synonyms: [total sales, revenue]
```

## Key Features

- **Strict validation** — all models reject unknown fields (`extra="forbid"`)
- **Referential integrity** — relationship `from`/`to` checked against dataset names
- **Column count alignment** — relationship `from_columns` and `to_columns` must match
- **AI-native** — `AIContext` at every level with instructions, synonyms, example queries
- **Multi-dialect** — expressions carry ANSI_SQL, Snowflake, Databricks, MDX, Tableau variants
- **String coercion** — bare strings in `ai_context` automatically wrapped into `AIContext` objects

## Development

```bash
pytest tests/ -v       # 70 tests
mypy osi/ --strict     # 0 errors
```

## License

Apache License 2.0
