"""Unit tests for the cart pricing logic.

These tests encode the agreed business rules. They are the contract -- if a
change breaks one of these, the change is wrong, not the test.
"""

import pytest

from src.cart import (
    FREE_SHIPPING_THRESHOLD,
    SHIPPING_FLAT_RATE,
    LineItem,
    apply_discount,
    cart_total,
    line_total,
    shipping_cost,
    subtotal,
    vat,
)


def test_line_total_multiplies_price_by_quantity():
    assert line_total(LineItem("SKU-1", 9.99, 3)) == pytest.approx(29.97)


def test_line_total_single_quantity():
    assert line_total(LineItem("SKU-1", 12.50, 1)) == pytest.approx(12.50)


def test_subtotal_sums_all_lines():
    items = [LineItem("A", 10.00, 2), LineItem("B", 5.00, 3)]
    assert subtotal(items) == pytest.approx(35.00)


def test_subtotal_of_empty_cart_is_zero():
    assert subtotal([]) == pytest.approx(0.0)


def test_apply_discount_takes_percentage_off():
    assert apply_discount(100.00, 10) == pytest.approx(90.00)


def test_apply_discount_of_zero_is_a_noop():
    assert apply_discount(42.00, 0) == pytest.approx(42.00)


def test_apply_discount_clamps_negative_percent():
    assert apply_discount(100.00, -25) == pytest.approx(100.00)


def test_apply_discount_clamps_percent_above_100():
    assert apply_discount(100.00, 150) == pytest.approx(0.00)


def test_shipping_is_charged_below_threshold():
    assert shipping_cost(FREE_SHIPPING_THRESHOLD - 0.01) == pytest.approx(
        SHIPPING_FLAT_RATE
    )


def test_shipping_is_free_at_threshold():
    assert shipping_cost(FREE_SHIPPING_THRESHOLD) == pytest.approx(0.0)


def test_shipping_is_free_above_threshold():
    assert shipping_cost(FREE_SHIPPING_THRESHOLD + 100) == pytest.approx(0.0)


def test_vat_is_twenty_percent():
    assert vat(100.00) == pytest.approx(20.00)


def test_cart_total_small_order_includes_shipping_and_vat():
    # goods 20.00 + shipping 4.99 = 24.99 taxable, VAT 5.00 -> 29.99
    items = [LineItem("A", 10.00, 2)]
    assert cart_total(items) == pytest.approx(29.99)


def test_cart_total_large_order_has_free_shipping():
    # goods 60.00, no shipping, VAT 12.00 -> 72.00
    items = [LineItem("A", 30.00, 2)]
    assert cart_total(items) == pytest.approx(72.00)


def test_cart_total_applies_discount_before_shipping_threshold():
    # goods 55.00 - 20% = 44.00, below threshold so shipping 4.99 applies,
    # taxable 48.99, VAT 9.80 -> 58.79
    items = [LineItem("A", 55.00, 1)]
    assert cart_total(items, percent_off=20) == pytest.approx(58.79)


def test_cart_total_of_empty_cart_is_shipping_plus_vat():
    assert cart_total([]) == pytest.approx(5.99)
