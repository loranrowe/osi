# osi-parser

[OSI (Open Semantic Interchange)](https://open-semantic-interchange.org/) v0.1.1 规范的极简 Python 实现——将语义模型 YAML/JSON 解析为带类型校验的 Pydantic 对象。

为数据分析 AI 智能体而构建，提供将语义模型加载到内存的可靠方式——是 NL2SQL、指标解析、语义查询生成的基础设施。

## 安装

```bash
pip install -e ".[dev]"
```

需要 Python >=3.11。

**依赖：** pydantic >=2.0, pyyaml >=6.0  
**开发依赖：** pytest >=8.0, mypy >=1.0

## 快速开始

```python
from osi import load_osi

# 一行加载语义模型
doc = load_osi("ecommerce_model.yaml")

model = doc.models[0]
print(model.name)                              # "ecommerce_analytics"
print(model.metrics[0].name)                   # "total_revenue"
print(model.metrics[0].ai_context.synonyms)    # ["total sales", "revenue"]

# 导航数据集
orders = model.datasets[0]
print(orders.source)                           # "sales.public.orders"
print(orders.fields[2].dimension.is_time)      # True

# 遍历关系
rel = model.relationships[0]
print(f"{rel.from_} -> {rel.to}")             # "orders -> customers"
```

## 包结构

```
osi/
  __init__.py      # 公开 API — 17 个导出
  enums.py         # Dialect、Vendor（str Enum）
  exceptions.py    # OsiError、OsiValidationError、OsiIntegrityError
  models.py        # 11 个 Pydantic 模型，从 DialectDef 到 SemanticModel
  parser.py        # load_osi() — YAML/JSON → OSIDocument
```

## 模型层级

| 模型 | 说明 |
|-------|------|
| `OSIDocument` | 顶层容器，包含语义模型列表 |
| `SemanticModel` | 完整模型：数据集 + 关系 + 指标 |
| `Dataset` | 逻辑表，含 name、source、字段、主键 |
| `Field` | 行级属性，支持多方言 SQL 表达式 |
| `Relationship` | 数据集间的外键关联 |
| `Metric` | 跨一个或多个数据集的聚合表达式 |
| `AIContext` | 面向 AI 工具的指令、同义词、问题示例 |
| `FieldExpression` / `DialectDef` | 多 SQL 方言表达式支持 |
| `DimensionMeta` | 维度元数据（如 is_time） |
| `CustomExtension` | 厂商专属元数据 |

## 公开 API

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

## OSI 模型示例（YAML）

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
          synonyms: [总销售额, 营收]
```

## 核心特性

- **严格校验** — 所有模型拒绝未定义字段（`extra="forbid"`）
- **引用完整性** — 关系的 `from`/`to` 自动校验是否引用已有数据集
- **列数对齐** — 关系的 `from_columns` 与 `to_columns` 长度必须一致
- **AI 原生** — `AIContext` 可挂载在任何层级，包含指令、同义词、示例问题
- **多方言** — 表达式可同时携带 ANSI_SQL、Snowflake、Databricks、MDX、Tableau 版本
- **字符串自动转换** — `ai_context` 传入裸字符串时自动包装为 `AIContext` 对象

## 与数据分析智能体结合

OSI 解决智能体 NL2SQL 场景中的语义对齐问题：

| 痛点 | OSI 的解法 |
|------|-----------|
| "营收"在不同 BI 工具里定义不同 | `Metric.ai_context.synonyms` 统一锚定 |
| 智能体不知道表之间怎么 JOIN | `Relationship` 显式定义关联路径 |
| SQL 方言不兼容 | `FieldExpression` 携带多方言版本 |
| 缺少业务上下文导致幻觉 | `AIContext.instructions` 提供引导 |

```python
# 智能体根据用户自然语言匹配指标
user_query = "查上个月的营收"
for metric in model.metrics:
    if any(s in user_query for s in metric.ai_context.synonyms):
        print(f"匹配指标: {metric.name}")
        print(f"SQL: {metric.expression.dialects[0].expression}")
```

## 开发

```bash
pytest tests/ -v       # 70 个测试
mypy osi/ --strict     # 0 错误
```

## 许可

Apache License 2.0
