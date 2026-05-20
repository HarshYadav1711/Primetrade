"""Order placement and response handling."""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import place_futures_order
from bot.logging_config import (
    get_order_logger,
    log_error,
    log_request,
    log_response,
)


class OrderError(Exception):
    """Order placement failed (API or network)."""


def place_order(client: Client, params: dict[str, str | float | None]) -> dict:
    """
    Place order via client and log request/response.
    Raises OrderError on API/request failure.
    """
    order_type = params["type"]
    logger = get_order_logger(order_type)
    log_request(logger, params)

    try:
        response = place_futures_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["type"],
            quantity=params["quantity"],
            price=params.get("price"),
        )
    except BinanceAPIException as e:
        log_error(logger, "Binance API error", e)
        msg = getattr(e, "message", None) or str(e)
        if "notional" in msg.lower() and "100" in msg:
            msg = (
                f"{msg} "
                "Order notional (quantity × price) must be at least 100 USDT. "
                "Use a larger quantity."
            )
        raise OrderError(msg) from e
    except BinanceRequestException as e:
        log_error(logger, "Binance request error", e)
        raise OrderError(str(e)) from e

    log_response(logger, response)
    return response


def format_order_summary(response: dict) -> str:
    """Human-readable order result (orderId, status, executedQty, avgPrice)."""

    def _field(label: str, value: object) -> str:
        display = value if value is not None and str(value).strip() else "—"
        return f"  {label:<13}{display}"

    lines = [
        _field("orderId:", response.get("orderId")),
        _field("status:", response.get("status")),
        _field("executedQty:", response.get("executedQty", response.get("origQty"))),
    ]
    avg = response.get("avgPrice")
    if avg is not None and str(avg).strip():
        lines.append(_field("avgPrice:", avg))
    return "\n".join(lines)
