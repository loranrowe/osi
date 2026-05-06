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
