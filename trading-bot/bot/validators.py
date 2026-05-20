"""Input validation for order parameters."""

import re

VALID_SIDES = frozenset({"BUY", "SELL"})
VALID_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "STOP_MARKET"})
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(Exception):
    """Raised when CLI input fails validation."""

    pass


def validate_symbol(symbol: str) -> str:
    """Symbol must be non-empty, alphanumeric, reasonable length (e.g. BTCUSDT)."""
    if not symbol or not symbol.strip():
        raise ValidationError("symbol: required (e.g. BTCUSDT)")
    s = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(s):
        raise ValidationError(
            "symbol: invalid format — use 5–20 uppercase letters and digits (e.g. BTCUSDT)"
        )
    return s


def validate_side(side: str) -> str:
    """Side must be BUY or SELL."""
    if not side or not side.strip():
        raise ValidationError("side: required — must be BUY or SELL")
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"side: must be BUY or SELL (got {side.strip()!r})")
    return s


def validate_order_type(order_type: str) -> str:
    """Order type must be MARKET, LIMIT, or STOP_MARKET."""
    if not order_type or not order_type.strip():
        raise ValidationError("order type: required — must be MARKET, LIMIT, or STOP_MARKET")
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"order type: must be MARKET, LIMIT, or STOP_MARKET (got {order_type.strip()!r})"
        )
    return t


def validate_quantity(quantity: str) -> float:
    """Quantity must be a positive number."""
    if not quantity or not str(quantity).strip():
        raise ValidationError("quantity: required — must be a positive number")
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(
            f"quantity: must be a positive number (invalid value {quantity!r})"
        )
    if q <= 0:
        raise ValidationError(
            f"quantity: must be greater than zero (got {quantity.strip()})"
        )
    return q


def validate_stop_price(stop_price: str | None, order_type: str) -> float | None:
    """Stop price required for STOP_MARKET; must be positive. Ignored for other types."""
    if order_type != "STOP_MARKET":
        return None
    if not stop_price or not str(stop_price).strip():
        raise ValidationError(
            "stop price: required for STOP_MARKET orders (pass --stop-price)"
        )
    try:
        p = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(
            f"stop price: must be a positive number (invalid value {stop_price!r})"
        )
    if p <= 0:
        raise ValidationError(
            f"stop price: must be greater than zero (got {stop_price.strip()})"
        )
    return p


def validate_price(price: str | None, order_type: str) -> float | None:
    """Price required for LIMIT; must be positive. Ignored for MARKET and STOP_MARKET."""
    if order_type != "LIMIT":
        return None
    if not price or not str(price).strip():
        raise ValidationError("price: required for LIMIT orders (pass --price)")
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"price: must be a positive number (invalid value {price!r})")
    if p <= 0:
        raise ValidationError(f"price: must be greater than zero (got {price.strip()})")
    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict[str, str | float | None]:
    """Validate all order parameters and return a normalized parameter dict."""
    order_type_n = validate_order_type(order_type)
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "type": order_type_n,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type_n),
        "stop_price": validate_stop_price(stop_price, order_type_n),
    }
