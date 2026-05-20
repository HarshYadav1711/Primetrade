"""Smoke tests for order input validation (no network, no mocks)."""

import unittest

from bot.validators import ValidationError, validate_order_params


class TestValidateOrderParams(unittest.TestCase):
    def test_market_order_normalizes_and_accepts_valid_input(self):
        result = validate_order_params(
            symbol="btcusdt",
            side="buy",
            order_type="market",
            quantity="0.002",
        )
        self.assertEqual(
            result,
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 0.002,
                "price": None,
            },
        )

    def test_limit_order_requires_positive_price(self):
        result = validate_order_params(
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity="0.04",
            price="2500",
        )
        self.assertEqual(result["type"], "LIMIT")
        self.assertEqual(result["price"], 2500.0)

    def test_invalid_symbol_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_order_params("btc", "BUY", "MARKET", "1")
        self.assertIn("symbol", str(ctx.exception).lower())

    def test_invalid_side_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_order_params("BTCUSDT", "HOLD", "MARKET", "1")
        self.assertIn("side", str(ctx.exception).lower())

    def test_non_positive_quantity_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_order_params("BTCUSDT", "BUY", "MARKET", "0")
        self.assertIn("quantity", str(ctx.exception).lower())

    def test_limit_without_price_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_order_params("BTCUSDT", "BUY", "LIMIT", "0.01")
        self.assertIn("price", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
