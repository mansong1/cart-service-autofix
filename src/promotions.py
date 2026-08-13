"""Promotional pricing rules.

Layered on top of the base cart pricing in `cart.py`. Kept separate because
promotions change often and the core pricing rules do not.
"""

from dataclasses import dataclass

from src.cart import LineItem, subtotal

BULK_THRESHOLD_UNITS = 10
BULK_DISCOUNT_PERCENT = 5.0
LOYALTY_TIERS = {
    "bronze": 0.0,
    "silver": 2.5,
    "gold": 5.0,
    "platinum": 7.5,
}
MAX_STACKED_PERCENT = 15.0


@dataclass(frozen=True)
class Promotion:
    code: str
    percent_off: float
    minimum_spend: float


def total_units(items: list[LineItem]) -> int:
    """Number of individual units across all lines."""
    return sum(i.quantity for i in items)


def bulk_discount_percent(items: list[LineItem]) -> float:
    """Percentage off earned purely from order size."""
    if total_units(items) >= BULK_THRESHOLD_UNITS:
        return BULK_DISCOUNT_PERCENT
    return 0.0


def loyalty_discount_percent(tier: str) -> float:
    """Percentage off earned from the customer's loyalty tier.

    Unknown tiers earn nothing rather than raising -- a bad tier string from
    upstream should not fail a checkout.
    """
    return LOYALTY_TIERS.get(tier.lower(), 0.0)


def promotion_discount_percent(items: list[LineItem], promo: Promotion | None) -> float:
    """Percentage off from an explicit promo code, if it qualifies."""
    if promo is None:
        return 0.0
    if subtotal(items) < promo.minimum_spend:
        return 0.0
    return promo.percent_off


def stacked_discount_percent(
    items: list[LineItem],
    tier: str = "bronze",
    promo: Promotion | None = None,
) -> float:
    """Combine every discount the order qualifies for.

    Discounts stack additively, then the total is capped at
    MAX_STACKED_PERCENT so no combination of promotions can ever give the
    order away below cost.
    """
    combined = (
        bulk_discount_percent(items)
        + loyalty_discount_percent(tier)
        + promotion_discount_percent(items, promo)
    )
    if combined > MAX_STACKED_PERCENT:
        return MAX_STACKED_PERCENT
    return combined
