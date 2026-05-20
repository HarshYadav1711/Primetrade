"""CLI entry point: argparse, confirmation, and output."""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import create_futures_client
from bot.orders import OrderError, format_order_summary, place_order
from bot.validators import ValidationError, validate_order_params

# ANSI styling when stderr/stdout is a TTY (no extra dependencies).
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"

_RULE = "─" * 44
_LABEL_WIDTH = 12


def _use_color(stream: object) -> bool:
    return hasattr(stream, "isatty") and stream.isatty()


def _style(text: str, *codes: str, stream: object = sys.stdout) -> str:
    if not codes or not _use_color(stream):
        return text
    return f"{''.join(codes)}{text}{_RESET}"


def _format_display_value(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return format(value, "g")
    return str(value)


def _order_field_rows(params: dict[str, str | float | None]) -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = [
        ("Symbol", params["symbol"]),
        ("Side", params["side"]),
        ("Type", params["type"]),
        ("Quantity", params["quantity"]),
    ]
    if params.get("price") is not None:
        rows.append(("Price", params["price"]))
    return rows


def _print_order_block(
    title: str,
    rows: list[tuple[str, object]],
    *,
    stream: object = sys.stdout,
    accent: str | None = None,
) -> None:
    width = max(_LABEL_WIDTH, max(len(label) for label, _ in rows))
    header = _style(title, _BOLD, accent or _CYAN, stream=stream) if accent else title
    print(file=stream)
    print(_style(_RULE, _DIM, stream=stream), file=stream)
    print(header, file=stream)
    print(_style(_RULE, _DIM, stream=stream), file=stream)
    for label, value in rows:
        print(
            f"  {label:<{width}}  {_format_display_value(value)}",
            file=stream,
        )
    print(_style(_RULE, _DIM, stream=stream), file=stream)


def _print_failure(title: str, detail: str) -> None:
    print(file=sys.stderr)
    print(_style(f"✗ {title}", _BOLD, _RED, stream=sys.stderr), file=sys.stderr)
    print(_style(_RULE, _DIM, stream=sys.stderr), file=sys.stderr)
    for line in detail.splitlines():
        print(f"  {line}", file=sys.stderr)
    print(_style(_RULE, _DIM, stream=sys.stderr), file=sys.stderr)
    print(file=sys.stderr)


def _print_success(response: dict) -> None:
    print()
    print(_style("✓ Order placed", _BOLD, _GREEN), "· Binance Futures Testnet")
    print(_style(_RULE, _DIM), file=sys.stdout)
    print(format_order_summary(response))
    print(_style(_RULE, _DIM), file=sys.stdout)
    print()


def _print_cancelled() -> None:
    print(_style("○ Order cancelled", _YELLOW), "— no request sent to the exchange.")


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
    _print_order_block(
        "Order preview · Binance Futures Testnet",
        _order_field_rows(params),
        accent=_CYAN,
    )
    prompt = _style(
        "Submit this order? [y/N] ",
        _BOLD,
        stream=sys.stdout,
    )
    hint = _style("  (y/yes to confirm · Enter or any other key to cancel)", _DIM)
    print(hint)
    print(prompt, end="", flush=True)
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
        _print_failure("Validation failed", str(e))
        return 1

    if not args.yes and not _confirm(params):
        print()
        _print_cancelled()
        return 0

    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        _print_failure(
            "Configuration error",
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set (e.g. in .env).",
        )
        return 1

    try:
        client = create_futures_client(api_key=api_key, api_secret=api_secret)
        response = place_order(client, params)
    except OrderError as e:
        _print_failure("Order failed", str(e))
        return 1
    except RuntimeError as e:
        _print_failure("Error", str(e))
        return 1
    except Exception as e:
        _print_failure("Unexpected error", str(e))
        return 1

    _print_success(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
