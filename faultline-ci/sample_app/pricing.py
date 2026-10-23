"""Invoice calculations using integer minor units, avoiding floating point money."""


def total_cents(unit_cents: int, quantity: int, discount_percent: int = 0) -> int:
    """Return a discounted line total, rounding down to a whole cent."""
    if unit_cents < 0 or quantity < 1:
        raise ValueError("Price must be nonnegative and quantity must be positive")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    subtotal = unit_cents * quantity
    return subtotal * (100 - discount_percent) // 100
