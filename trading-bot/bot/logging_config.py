"""File logging for market, limit, and stop-market orders."""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
MARKET_LOG = LOG_DIR / "market_order.log"
LIMIT_LOG = LOG_DIR / "limit_order.log"
STOP_MARKET_LOG = LOG_DIR / "stop_market_order.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_order_logger(order_type: str) -> logging.Logger:
    """Return a file logger for the given order type (one log file per type)."""
    _ensure_log_dir()
    name = f"bot.{order_type.lower()}_order"
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    kind = order_type.upper()
    if kind == "LIMIT":
        path = LIMIT_LOG
    elif kind == "STOP_MARKET":
        path = STOP_MARKET_LOG
    else:
        path = MARKET_LOG
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    return logger


def _order_tags(params: dict) -> str:
    """symbol/side/type tags shared across request, response, and error lines."""
    parts: list[str] = []
    for key in ("symbol", "side", "type"):
        value = params.get(key)
        if value is not None and str(value).strip():
            parts.append(f"{key}={value}")
    return " ".join(parts)


def _merge_order_context(response: dict, params: dict | None) -> dict:
    """Prefer exchange response fields; fall back to outgoing request params."""
    merged = dict(params or {})
    for key in ("symbol", "side", "type"):
        value = response.get(key)
        if value is not None and str(value).strip():
            merged[key] = value
    return merged


def _response_order_id(response: dict) -> object:
    """Standard orders use orderId; STOP_MARKET algo orders use algoId."""
    if response.get("orderId") is not None:
        return response.get("orderId")
    return response.get("algoId")


def _response_status(response: dict) -> object:
    return response.get("status") or response.get("algoStatus")


def _execution_tags(response: dict) -> str:
    """Execution identifiers when the exchange returns them."""
    parts: list[str] = []
    order_id = _response_order_id(response)
    if order_id is not None:
        parts.append(f"orderId={order_id}")
    client_order_id = response.get("clientOrderId") or response.get("clientAlgoId")
    if client_order_id:
        parts.append(f"clientOrderId={client_order_id}")
    return " ".join(parts)


def log_request(logger: logging.Logger, params: dict) -> None:
    """Log outgoing order parameters (no API keys or secrets)."""
    tags = _order_tags(params)
    logger.info(
        "order | request | %s | status=submitting | %s",
        tags or "—",
        params,
    )


def log_response(
    logger: logging.Logger, response: dict, params: dict | None = None
) -> None:
    """Log exchange response summary fields."""
    tags = _order_tags(_merge_order_context(response, params))
    execution = _execution_tags(response)
    status = _response_status(response)
    executed_qty = response.get("executedQty", response.get("origQty"))
    logger.info(
        "order | response | %s | %s | status=%s executedQty=%s",
        tags or "—",
        execution or "orderId=—",
        status,
        executed_qty,
    )


def log_error(
    logger: logging.Logger,
    context: str,
    exc: Exception | None = None,
    *,
    params: dict | None = None,
) -> None:
    """Log a failure; include stack trace when *exc* is provided."""
    tags = _order_tags(params or {})
    detail = f"status=failed | {context}"
    if exc is not None and getattr(exc, "code", None):
        detail = f"{detail} | apiCode={exc.code}"
    message = f"order | failed | {tags} | {detail}" if tags else f"order | failed | {detail}"
    if exc is not None:
        logger.exception(message)
    else:
        logger.error(message)

