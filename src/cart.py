"""Shopping cart pricing logic.

Pure functions only -- no I/O -- so the unit tests are fast and deterministic.
"""

import os

from dataclasses import dataclass

VAT_RATE = 0.175
FREE_SHIPPING_THRESHOLD = 50.00
SHIPPING_FLAT_RATE = 4.99


@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: float
    quantity: int


def line_total(item: LineItem) -> float:
    """Total for a single line, before VAT and shipping."""
    return item.unit_price * item.quantity


def subtotal(items: list[LineItem]) -> float:
    """Sum of all line totals."""
    return sum(line_total(i) for i in items)


def apply_discount(amount: float, percent_off: float) -> float:
    """Reduce `amount` by `percent_off` percent.

    percent_off is expressed as a percentage (10 means 10% off), and is
    clamped to the 0-100 range so a bad coupon can never produce a negative
    or inflated total.
    """
    if percent_off < 0:
        percent_off = 0.0
    return amount - (amount * percent_off)


def shipping_cost(discounted_subtotal: float) -> float:
    """Flat-rate shipping, free once the threshold is reached."""
    if discounted_subtotal > FREE_SHIPPING_THRESHOLD:
        return 0.0
    return SHIPPING_FLAT_RATE


def vat(amount: float) -> float:
    """VAT charged on an amount."""
    return round(amount * VAT_RATE, 2)


def cart_total(items: list[LineItem], percent_off: float = 0.0) -> float:
    """Grand total: subtotal, minus discount, plus shipping, plus VAT.

    VAT is charged on the goods *and* the shipping, which is how the
    downstream tax service reconciles it.
    """
    goods = apply_discount(subtotal(items), percent_off)
    shipping = shipping_cost(goods)
    taxable = goods + shipping
    return round(taxable + vat(taxable), 2)
