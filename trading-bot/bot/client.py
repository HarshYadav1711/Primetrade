"""Binance USDT-M Futures client wrapper (testnet only)."""

from binance.client import Client

# USDT-M Futures Testnet REST base (python-binance Client.FUTURES_TESTNET_URL).
# With testnet=True, futures_create_order POSTs to {base}/v1/order.
FUTURES_TESTNET_FAPI_BASE: str = Client.FUTURES_TESTNET_URL
FUTURES_TESTNET_ORDER_ENDPOINT: str = (
    f"{FUTURES_TESTNET_FAPI_BASE}/{Client.FUTURES_API_VERSION}/order"
)


def _futures_order_endpoint(client: Client) -> str:
    """Build the v1 futures order path from public SDK URL constants."""
    base = client.FUTURES_TESTNET_URL if client.testnet else client.FUTURES_URL
    return f"{base}/{client.FUTURES_API_VERSION}/order"


def _assert_futures_testnet_client(client: Client) -> None:
    """Ensure the client is testnet-only before any futures order call."""
    if not client.testnet:
        raise RuntimeError("Binance client must be initialized with testnet=True.")
    endpoint = _futures_order_endpoint(client)
    if endpoint != FUTURES_TESTNET_ORDER_ENDPOINT:
        raise RuntimeError(
            f"Futures order endpoint is not testnet: {endpoint!r} "
            f"(expected {FUTURES_TESTNET_ORDER_ENDPOINT!r})"
        )


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
    _assert_futures_testnet_client(client)
    return client


def place_futures_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> dict:
    """
    Place a single futures order. MARKET, LIMIT, or STOP_MARKET.
    LIMIT requires price and timeInForce GTC; STOP_MARKET requires stopPrice.
    """
    params: dict[str, str | float] = {
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
    elif order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        params["stopPrice"] = stop_price
    return client.futures_create_order(**params)
