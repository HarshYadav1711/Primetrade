# Trading Bot (Binance Futures Testnet)

CLI tool to place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M). No strategy logic; order execution only.

## Features

- Place MARKET and LIMIT orders on Binance Futures Testnet
- BUY and SELL supported
- Input validation (symbol, side, type, quantity, price for LIMIT)
- Confirmation prompt before sending (skippable with `--yes`)
- Structured logging to `logs/market_order.log` and `logs/limit_order.log`
- Clear CLI output: request summary, then order response (orderId, status, executedQty, avgPrice)

## Tech stack

- Python 3.10+
- python-binance (Futures API)
- argparse, python-dotenv, logging

## Setup

For detailed step-by-step instructions (creating API keys and running the project), see **[SETUP.md](SETUP.md)**.

1. Create a virtualenv and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set your testnet keys:

   ```bash
   copy .env.example .env
   ```

   Get API key and secret from [Binance Futures Testnet](https://testnet.binancefuture.com). No real funds; testnet only.

3. Run from the project root (so `bot` and `logs` resolve correctly). Notional must be ≥ 100 USDT; for BTC use at least `0.002`:

   ```bash
   python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
   ```

## CLI usage

Required: `--symbol`, `--side`, `--type`, `--quantity`. For LIMIT orders you must pass `--price`.

Examples (notional = quantity × price must be ≥ 100 USDT):

```text
# Market buy
python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002

# Limit sell (0.01 ETH × 2500 = 25 USDT is below 100; use e.g. 0.04 for ~100)
python run.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.04 --price 2500

# Skip confirmation
python run.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.002 -y
```

Help:

```text
python run.py --help
```

## Logging

- Logs go under the `logs/` directory.
- Market orders: `logs/market_order.log`
- Limit orders: `logs/limit_order.log`
- Each line has timestamp, level, and message. Requests and responses are logged; errors are logged with details. No secrets in logs.

## Assumptions

- Binance Futures Testnet only; no mainnet.
- USDT-M (linear) contracts only.
- API key/secret are in `.env`; no other config file required.
- Running from project root so imports and `logs/` path work as intended.
