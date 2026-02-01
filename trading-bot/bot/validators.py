"""Input validation for order parameters."""

import re

VALID_SIDES = frozenset({"BUY", "SELL"})
VALID_ORDER_TYPES = frozenset({"MARKET", "LIMIT"})
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(Exception):
    """Raised when CLI input fails validation."""

    pass


def validate_symbol(symbol: str) -> str:
    """Symbol must be non-empty, alphanumeric, reasonable length (e.g. BTCUSDT)."""
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol is required.")
    s = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(s):
        raise ValidationError(
            "Invalid symbol format. Use a valid trading pair (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    """Side must be BUY or SELL."""
    if not side or not side.strip():
        raise ValidationError("Side is required.")
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError("Side must be BUY or SELL.")
    return s


def validate_order_type(order_type: str) -> str:
    """Order type must be MARKET or LIMIT."""
    if not order_type or not order_type.strip():
        raise ValidationError("Order type is required.")
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError("Order type must be MARKET or LIMIT.")
    return t


def validate_quantity(quantity: str) -> float:
    """Quantity must be a positive number."""
    if not quantity or not str(quantity).strip():
        raise ValidationError("Quantity is required.")
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a number.")
    if q <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    return q


def validate_price(price: str | None, order_type: str) -> float | None:
    """Price required for LIMIT; must be positive. Ignored for MARKET."""
    if order_type == "MARKET":
        return None
    if not price or not str(price).strip():
        raise ValidationError("Price is required for LIMIT orders.")
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError("Price must be a number.")
    if p <= 0:
        raise ValidationError("Price must be greater than zero.")
    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> dict:
    """Validate all order parameters and return normalized dict."""
    order_type_n = validate_order_type(order_type)
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "type": order_type_n,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type_n),
    }
