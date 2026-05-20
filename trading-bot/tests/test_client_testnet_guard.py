"""Smoke tests for Futures Testnet client guards (public SDK surface only)."""

import unittest

from binance.client import Client

from bot.client import (
    FUTURES_TESTNET_ORDER_ENDPOINT,
    _assert_futures_testnet_client,
    _futures_order_endpoint,
    create_futures_client,
)


class TestFuturesTestnetGuard(unittest.TestCase):
    def test_create_futures_client_enables_testnet(self):
        client = create_futures_client("key", "secret")
        self.assertTrue(client.testnet)

    def test_order_endpoint_uses_public_testnet_constants(self):
        client = Client("key", "secret", testnet=True, ping=False)
        self.assertEqual(_futures_order_endpoint(client), FUTURES_TESTNET_ORDER_ENDPOINT)

    def test_assert_rejects_non_testnet_client(self):
        client = Client("key", "secret", testnet=False, ping=False)
        with self.assertRaises(RuntimeError) as ctx:
            _assert_futures_testnet_client(client)
        self.assertIn("testnet", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
