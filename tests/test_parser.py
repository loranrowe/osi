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
    with pytest.raises(OsiValidationError):
        load_osi(FIXTURES / "invalid_schema.yaml")
