"""Domain logic services for orders and calculations."""

from typing import Any


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price with validation."""
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not (0 <= discount_percent <= 100):
        raise ValueError("Discount percent must be between 0 and 100")

    discount_amount = price * (discount_percent / 100.0)
    return round(price - discount_amount, 2)


def process_order_summary(
    items: list[dict[str, Any]], tax_rate: float = 0.08
) -> dict[str, Any]:
    """Calculate subtotal, tax, and total for an order."""
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    return {
        "item_count": sum(item["quantity"] for item in items),
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
    }
