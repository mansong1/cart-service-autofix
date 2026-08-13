"""Unit tests for bulk pricing tiers.

Same contract rule as test_cart.py: these encode the agreed behaviour.
"""

import pytest

from src.bulk import bulk_discount_percent, bulk_line_total
from src.cart import LineItem, cart_total


def test_no_bulk_discount_below_first_tier():
    assert bulk_discount_percent(9) == pytest.approx(0.0)


def test_first_tier_at_ten():
    assert bulk_discount_percent(10) == pytest.approx(5.0)


def test_best_tier_wins():
    assert bulk_discount_percent(60) == pytest.approx(15.0)


def test_bulk_line_total_applies_tier():
    # 10 x 20.00 = 200.00, less 5% = 190.00
    assert bulk_line_total(LineItem("A", 20.00, 10)) == pytest.approx(190.00)


def test_bulk_line_total_no_discount_for_single_item():
    assert bulk_line_total(LineItem("A", 20.00, 1)) == pytest.approx(20.00)


def test_cart_total_charges_vat_on_discounted_goods():
    # 100.00 of goods, 10% coupon -> 90.00 goods, free shipping at that value,
    # VAT 18.00 -> 108.00. VAT must follow the discount, not the list price.
    items = [LineItem("A", 50.00, 2)]
    assert cart_total(items, percent_off=10) == pytest.approx(108.00)
