"""Focused tests for order placement and response formatting (mocked, no network)."""

import json
import unittest
from unittest.mock import MagicMock, patch

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.orders import OrderError, format_order_summary, place_order

MARKET_PARAMS = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.002,
    "price": None,
    "stop_price": None,
}

LIMIT_PARAMS = {
    "symbol": "ETHUSDT",
    "side": "SELL",
    "type": "LIMIT",
    "quantity": 0.04,
    "price": 2500.0,
    "stop_price": None,
}

STOP_MARKET_PARAMS = {
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "STOP_MARKET",
    "quantity": 0.002,
    "price": None,
    "stop_price": 90000.0,
}


def _binance_api_exception(message: str, *, code: int = -1111) -> BinanceAPIException:
    response = MagicMock()
    response.text = json.dumps({"code": code, "msg": message})
    return BinanceAPIException(response, 400, response.text)


@patch("bot.orders.get_order_logger")
@patch("bot.orders.place_futures_order")
class TestPlaceOrderPayload(unittest.TestCase):
    def test_market_order_forwards_correct_payload(self, mock_place, _mock_logger):
        mock_place.return_value = {"orderId": 1, "status": "FILLED"}
        client = MagicMock()

        place_order(client, MARKET_PARAMS)

        mock_place.assert_called_once_with(
            client=client,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.002,
            price=None,
            stop_price=None,
        )

    def test_limit_order_forwards_correct_payload(self, mock_place, _mock_logger):
        mock_place.return_value = {"orderId": 2, "status": "NEW"}
        client = MagicMock()

        place_order(client, LIMIT_PARAMS)

        mock_place.assert_called_once_with(
            client=client,
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=0.04,
            price=2500.0,
            stop_price=None,
        )

    def test_stop_market_order_forwards_correct_payload(self, mock_place, _mock_logger):
        mock_place.return_value = {"orderId": 3, "status": "NEW"}
        client = MagicMock()

        place_order(client, STOP_MARKET_PARAMS)

        mock_place.assert_called_once_with(
            client=client,
            symbol="BTCUSDT",
            side="SELL",
            order_type="STOP_MARKET",
            quantity=0.002,
            price=None,
            stop_price=90000.0,
        )


@patch("bot.orders.get_order_logger")
@patch("bot.orders.place_futures_order")
class TestPlaceOrderExceptions(unittest.TestCase):
    def test_binance_api_exception_wraps_as_order_error(self, mock_place, _mock_logger):
        mock_place.side_effect = _binance_api_exception("Insufficient balance")
        with self.assertRaises(OrderError) as ctx:
            place_order(MagicMock(), MARKET_PARAMS)
        self.assertEqual(str(ctx.exception), "Insufficient balance")

    def test_notional_api_error_appends_usdt_hint(self, mock_place, _mock_logger):
        mock_place.side_effect = _binance_api_exception(
            "Order's notional must be no smaller than 100"
        )
        with self.assertRaises(OrderError) as ctx:
            place_order(MagicMock(), LIMIT_PARAMS)
        msg = str(ctx.exception)
        self.assertIn("notional", msg.lower())
        self.assertIn("100 USDT", msg)

    def test_binance_request_exception_wraps_as_order_error(
        self, mock_place, _mock_logger
    ):
        mock_place.side_effect = BinanceRequestException("Connection timed out")
        with self.assertRaises(OrderError) as ctx:
            place_order(MagicMock(), MARKET_PARAMS)
        self.assertIn("Connection timed out", str(ctx.exception))


class TestFormatOrderSummary(unittest.TestCase):
    def test_formats_filled_market_response(self):
        summary = format_order_summary(
            {
                "orderId": 12345,
                "status": "FILLED",
                "executedQty": "0.002",
                "avgPrice": "95000.50",
            }
        )
        self.assertIn("Order ID", summary)
        self.assertIn("12345", summary)
        self.assertIn("FILLED", summary)
        self.assertIn("0.002", summary)
        self.assertIn("95000.50", summary)
        self.assertIn("Avg Price", summary)

    def test_omits_avg_price_when_missing_or_blank(self):
        without_key = format_order_summary(
            {"orderId": 1, "status": "NEW", "executedQty": "0"}
        )
        blank = format_order_summary(
            {"orderId": 1, "status": "NEW", "executedQty": "0", "avgPrice": ""}
        )
        self.assertNotIn("Avg Price", without_key)
        self.assertNotIn("Avg Price", blank)

    def test_falls_back_to_orig_qty(self):
        summary = format_order_summary(
            {"orderId": 9, "status": "NEW", "origQty": "0.04"}
        )
        self.assertIn("0.04", summary)

    def test_displays_dash_for_missing_order_id(self):
        summary = format_order_summary({"status": "NEW"})
        self.assertIn("—", summary)


if __name__ == "__main__":
    unittest.main()
