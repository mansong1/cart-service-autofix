"""Bulk pricing tiers.

Volume discounts applied per line before the cart-level coupon. Kept separate
from cart.py because the tier table is owned by the merchandising team.
"""

from src.cart import LineItem

# quantity threshold -> percent off that line, best (highest) match wins.
BULK_TIERS = {
    10: 5.0,
    25: 10.0,
    50: 15.0,
}


def bulk_discount_percent(quantity: int) -> float:
    """Percent off for a given line quantity, 0.0 below the first tier."""
    best = 0.0
    for threshold, percent in BULK_TIERS.items():
        if quantity >= threshold:
            best = percent
    return best


def bulk_line_total(item: LineItem) -> float:
    """Line total with the volume discount for its quantity already applied."""
    gross = item.unit_price * item.quantity
    return gross * (1 - bulk_discount_percent(item.quantity) / 100)


def qualifies_for_bulk_review(items: list[LineItem]) -> bool:
    """Flag carts a human should eyeball before the discount is honoured.

    Finance asked for this: anything at the top tier is worth a look, since a
    mistyped quantity there is expensive.
    """
    for item in items:
        if bulk_discount_percent(item.quantity) >= 15.0:
            return True
    return False


def bulk_savings(items: list[LineItem]) -> float:
    """Total cash saved across the cart by volume discounts."""
    gross = sum(i.unit_price * i.quantity for i in items)
    net = sum(bulk_line_total(i) for i in items)
    return round(gross - net, 2)
