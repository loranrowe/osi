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
