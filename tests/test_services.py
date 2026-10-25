"""Unit tests for domain calculation services."""

import pytest

from src.app.services import calculate_discount, process_order_summary


def test_calculate_discount_valid():
    assert calculate_discount(100.0, 10.0) == 90.0
    assert calculate_discount(50.0, 0.0) == 50.0
    assert calculate_discount(200.0, 100.0) == 0.0
    assert calculate_discount(99.99, 15.0) == 84.99


def test_calculate_discount_invalid_price():
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_discount(-10.0, 10.0)


def test_calculate_discount_invalid_percent():
    with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
        calculate_discount(100.0, 150.0)
    with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
        calculate_discount(100.0, -5.0)


def test_process_order_summary():
    items = [
        {"name": "Widget A", "price": 10.0, "quantity": 2},  # 20.0
        {"name": "Widget B", "price": 15.0, "quantity": 1},  # 15.0
    ]
    summary = process_order_summary(items, tax_rate=0.10)
    assert summary["item_count"] == 3
    assert summary["subtotal"] == 35.0
    assert summary["tax"] == 3.50
    assert summary["total"] == 38.50


def test_process_order_summary_invalid_tax():
    items = [{"name": "Widget A", "price": 10.0, "quantity": 1}]
    with pytest.raises(ValueError, match="Tax rate cannot be negative"):
        process_order_summary(items, tax_rate=-0.05)
