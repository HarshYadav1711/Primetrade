"""Smoke tests for futures order payload construction (in-process fake client)."""

import unittest

from bot.client import place_futures_order


class _RecordingClient:
    """Minimal stand-in; lives only in tests."""

    def __init__(self):
        self.last_kwargs = None

    def futures_create_order(self, **kwargs):
        self.last_kwargs = kwargs
        return {"orderId": 1, "status": "NEW"}


class TestPlaceFuturesOrderPayload(unittest.TestCase):
    def test_market_order_payload_excludes_limit_fields(self):
        client = _RecordingClient()
        place_futures_order(
            client,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.002,
        )
        self.assertEqual(
            client.last_kwargs,
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 0.002,
            },
        )
        self.assertNotIn("price", client.last_kwargs)
        self.assertNotIn("timeInForce", client.last_kwargs)

    def test_limit_order_payload_includes_price_and_gtc(self):
        client = _RecordingClient()
        place_futures_order(
            client,
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=0.04,
            price=2500.0,
        )
        self.assertEqual(
            client.last_kwargs,
            {
                "symbol": "ETHUSDT",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": 0.04,
                "timeInForce": "GTC",
                "price": 2500.0,
            },
        )

    def test_limit_without_price_raises_before_api_call(self):
        client = _RecordingClient()
        with self.assertRaises(ValueError):
            place_futures_order(
                client,
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity=0.01,
                price=None,
            )
        self.assertIsNone(client.last_kwargs)


if __name__ == "__main__":
    unittest.main()
