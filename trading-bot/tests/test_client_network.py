"""Tests for Binance client network timeout and transient retry (no live orders)."""

import json
import unittest
from unittest.mock import MagicMock, patch

import requests
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import (
    MAX_NETWORK_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
    _call_with_transient_retry,
    create_futures_client,
    place_futures_order,
)


class _FlakyClient:
    def __init__(self, errors_before_success: int):
        self.calls = 0
        self._errors_before_success = errors_before_success

    def futures_create_order(self, **_kwargs):
        self.calls += 1
        if self.calls <= self._errors_before_success:
            raise requests.exceptions.ConnectionError("reset by peer")
        return {"orderId": 1, "status": "NEW"}


class TestCreateFuturesClientTimeout(unittest.TestCase):
    def test_client_uses_explicit_request_timeout(self):
        client = create_futures_client("key", "secret")
        self.assertEqual(client._requests_params, {"timeout": REQUEST_TIMEOUT_SECONDS})


class TestTransientRetry(unittest.TestCase):
    def test_retries_then_succeeds(self):
        client = _FlakyClient(errors_before_success=1)
        with patch("bot.client.time.sleep"):
            response = place_futures_order(
                client,
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                quantity=0.002,
            )
        self.assertEqual(response["orderId"], 1)
        self.assertEqual(client.calls, 2)

    def test_exhausted_retries_reraise_same_exception(self):
        client = _FlakyClient(errors_before_success=MAX_NETWORK_RETRIES + 1)
        with patch("bot.client.time.sleep"):
            with self.assertRaises(requests.exceptions.ConnectionError):
                place_futures_order(
                    client,
                    symbol="BTCUSDT",
                    side="BUY",
                    order_type="MARKET",
                    quantity=0.002,
                )
        self.assertEqual(client.calls, MAX_NETWORK_RETRIES + 1)

    def test_binance_api_exception_not_retried(self):
        response = MagicMock()
        response.text = json.dumps({"code": -1111, "msg": "reject"})
        api_error = BinanceAPIException(response, 400, response.text)
        calls = {"n": 0}

        def raise_api():
            calls["n"] += 1
            raise api_error

        with self.assertRaises(BinanceAPIException):
            _call_with_transient_retry(raise_api)
        self.assertEqual(calls["n"], 1)

    def test_binance_request_exception_not_retried(self):
        calls = {"n": 0}

        def raise_request():
            calls["n"] += 1
            raise BinanceRequestException("Invalid Response: not json")

        with self.assertRaises(BinanceRequestException):
            _call_with_transient_retry(raise_request)
        self.assertEqual(calls["n"], 1)


if __name__ == "__main__":
    unittest.main()
