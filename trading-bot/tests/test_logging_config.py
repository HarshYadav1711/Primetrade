"""Tests for order log message formatting (in-memory, no files)."""

import logging
import unittest
from unittest.mock import MagicMock

from bot.logging_config import log_error, log_request, log_response


class _CaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class TestLogMessageFormat(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test.logging")
        self.logger.handlers.clear()
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        self.handler = _CaptureHandler()
        self.logger.addHandler(self.handler)

    def test_request_includes_symbol_side_type_and_status(self):
        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 0.002,
            "price": None,
        }
        log_request(self.logger, params)
        msg = self.handler.messages[0]
        self.assertIn("order | request |", msg)
        self.assertIn("symbol=BTCUSDT", msg)
        self.assertIn("side=BUY", msg)
        self.assertIn("type=MARKET", msg)
        self.assertIn("status=submitting", msg)
        self.assertIn(str(params), msg)

    def test_response_includes_execution_ids_and_status(self):
        response = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "orderId": 99,
            "clientOrderId": "cid-1",
            "status": "FILLED",
            "executedQty": "0.002",
        }
        log_response(self.logger, response)
        msg = self.handler.messages[0]
        self.assertIn("order | response |", msg)
        self.assertIn("symbol=BTCUSDT", msg)
        self.assertIn("orderId=99", msg)
        self.assertIn("clientOrderId=cid-1", msg)
        self.assertIn("status=FILLED", msg)
        self.assertIn("executedQty=0.002", msg)

    def test_error_includes_context_tags_and_api_code(self):
        params = {"symbol": "ETHUSDT", "side": "SELL", "type": "LIMIT", "quantity": 0.04}
        exc = MagicMock()
        exc.code = -1111
        log_error(self.logger, "binance api", exc, params=params)
        msg = self.handler.messages[0]
        self.assertIn("order | failed |", msg)
        self.assertIn("symbol=ETHUSDT", msg)
        self.assertIn("status=failed", msg)
        self.assertIn("binance api", msg)
        self.assertIn("apiCode=-1111", msg)


if __name__ == "__main__":
    unittest.main()
