"""Binance USDT-M Futures client wrapper (testnet only)."""

import time
from collections.abc import Callable
from typing import TypeVar

import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# USDT-M Futures Testnet REST base (python-binance Client.FUTURES_TESTNET_URL).
# With testnet=True, futures_create_order POSTs to {base}/v1/order.
FUTURES_TESTNET_FAPI_BASE: str = Client.FUTURES_TESTNET_URL
FUTURES_TESTNET_ORDER_ENDPOINT: str = (
    f"{FUTURES_TESTNET_FAPI_BASE}/{Client.FUTURES_API_VERSION}/order"
)

# Explicit HTTP timeout (seconds) passed to python-binance for every REST call.
REQUEST_TIMEOUT_SECONDS: float = 10.0

# Additional attempts after the first failure for transient network errors only.
MAX_NETWORK_RETRIES: int = 2

# Pause before each retry (seconds); linear backoff per attempt.
RETRY_BACKOFF_SECONDS: float = 0.5

_TRANSIENT_REQUEST_ERRORS: tuple[type[BaseException], ...] = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)

T = TypeVar("T")


def _call_with_transient_retry(func: Callable[[], T]) -> T:
    """Retry *func* only on transient ``requests`` transport failures."""
    last_exc: BaseException | None = None
    for attempt in range(MAX_NETWORK_RETRIES + 1):
        try:
            return func()
        except _TRANSIENT_REQUEST_ERRORS as exc:
            last_exc = exc
            if attempt >= MAX_NETWORK_RETRIES:
                raise
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry loop exited without result")  # pragma: no cover


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
        ping=False,
        requests_params={"timeout": REQUEST_TIMEOUT_SECONDS},
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
        # Binance Futures uses stopPrice as the trigger; execution is at market.
        if stop_price is None:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        params["stopPrice"] = stop_price

    def _create_order() -> dict:
        return client.futures_create_order(**params)

    return _call_with_transient_retry(_create_order)
