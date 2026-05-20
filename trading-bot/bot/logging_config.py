"""Structured logging for market, limit, and stop-market orders."""

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


def log_request(logger: logging.Logger, params: dict) -> None:
    """Log outgoing order parameters (no API keys or secrets)."""
    logger.info("order | request | %s", params)


def log_response(logger: logging.Logger, response: dict) -> None:
    """Log exchange response summary fields."""
    logger.info(
        "order | response | orderId=%s status=%s executedQty=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
    )


def log_error(logger: logging.Logger, context: str, exc: Exception | None = None) -> None:
    """Log a failure; include stack trace when *exc* is provided."""
    if exc is not None:
        logger.exception("order | failed | %s", context)
    else:
        logger.error("order | failed | %s", context)
