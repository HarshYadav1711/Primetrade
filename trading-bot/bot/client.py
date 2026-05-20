"""Binance USDT-M Futures client wrapper (testnet only)."""

from binance.client import Client

# USDT-M Futures Testnet REST base (python-binance BaseClient.FUTURES_TESTNET_URL).
# With testnet=True, futures_create_order POSTs to {base}/v1/order.
FUTURES_TESTNET_FAPI_BASE: str = Client.FUTURES_TESTNET_URL


def create_futures_client(api_key: str, api_secret: str) -> Client:
    """
    Build a python-binance Client for Binance USDT-M Futures Testnet only.

    ``testnet=True`` selects ``FUTURES_TESTNET_URL`` for all ``futures_*`` REST
    calls. This project only uses ``futures_create_order``, which resolves to
    ``{FUTURES_TESTNET_FAPI_BASE}/v1/order`` (not mainnet ``fapi.binance.com``).
    """
    client = Client(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True,
    )
    if not client.testnet:
        raise RuntimeError("Binance client must be initialized with testnet=True.")
    order_url = client._create_futures_api_uri("order")
    if not order_url.startswith(FUTURES_TESTNET_FAPI_BASE):
        raise RuntimeError(
            f"Futures order URL is not testnet: {order_url!r} "
            f"(expected prefix {FUTURES_TESTNET_FAPI_BASE!r})"
        )
    return client


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
