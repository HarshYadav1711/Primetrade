"""Binance USDT-M Futures client wrapper (testnet only)."""

from binance.client import Client


def create_futures_client(api_key: str, api_secret: str) -> Client:
    """Build a Binance Client pointed at Futures Testnet."""
    return Client(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True,
    )


def place_futures_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> dict:
    """
    Place a single futures order. MARKET or LIMIT.
    For LIMIT, price and timeInForce GTC are required.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        params["timeInForce"] = "GTC"
        params["price"] = price
    return client.futures_create_order(**params)
