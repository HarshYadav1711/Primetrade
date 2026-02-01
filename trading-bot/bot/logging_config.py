"""Structured logging for market and limit orders."""

import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
MARKET_LOG = LOG_DIR / "market_order.log"
LIMIT_LOG = LOG_DIR / "limit_order.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_order_logger(order_type: str) -> logging.Logger:
    """Return a logger that writes to the appropriate order log file."""
    _ensure_log_dir()
    name = f"bot.{order_type.lower()}_order"
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    path = LIMIT_LOG if order_type.upper() == "LIMIT" else MARKET_LOG
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    return logger


def log_request(logger: logging.Logger, params: dict) -> None:
    """Log outgoing order request (no secrets)."""
    logger.info("Request: %s", params)


def log_response(logger: logging.Logger, response: dict) -> None:
    """Log API response summary."""
    logger.info(
        "Response: orderId=%s status=%s executedQty=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
    )


def log_error(logger: logging.Logger, message: str, exc: Exception | None = None) -> None:
    """Log an error; optionally include exception."""
    if exc:
        logger.exception("%s: %s", message, exc)
    else:
        logger.error("%s", message)
