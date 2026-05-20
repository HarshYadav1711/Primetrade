"""CLI entry point: argparse, confirmation, and output."""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import create_futures_client
from bot.orders import OrderError, format_order_summary, place_order
from bot.validators import ValidationError, validate_order_params


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
  python run.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.04 --price 2500
        """,
    )
    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair (e.g. BTCUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT"],
        metavar="TYPE",
        help="Order type",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        metavar="QTY",
        help="Order quantity (positive number)",
    )
    parser.add_argument(
        "--price",
        default=None,
        metavar="PRICE",
        help="Limit price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    return parser.parse_args()


def _confirm(params: dict[str, str | float | None]) -> bool:
    """Return True if user confirms, False otherwise."""

    def _line(label: str, value: object) -> None:
        print(f"  {label:<10}{value}")

    print("\nOrder summary:")
    _line("symbol:", params["symbol"])
    _line("side:", params["side"])
    _line("type:", params["type"])
    _line("quantity:", params["quantity"])
    if params.get("price") is not None:
        _line("price:", params["price"])
    print("\nPlace this order on Binance Futures Testnet? [y/N] ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


def main() -> int:
    args = _parse_args()
    try:
        params = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1

    if not args.yes and not _confirm(params):
        print("Cancelled.")
        return 0

    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print(
            "Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set (e.g. in .env).",
            file=sys.stderr,
        )
        return 1

    try:
        client = create_futures_client(api_key=api_key, api_secret=api_secret)
        response = place_order(client, params)
    except OrderError as e:
        print(f"Order failed: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    print("\nOrder placed successfully:")
    print(format_order_summary(response))
    return 0


if __name__ == "__main__":
    sys.exit(main())
