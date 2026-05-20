
# Binance Futures Testnet Trading Bot

## Overview

This project is a simplified command-line trading utility built using Python for **Binance Futures USDT-M Testnet only**. It does not connect to Binance mainnet or spot markets.

The goal of the application is not to implement trading strategies or market analysis, but to demonstrate how a real trading system handles order execution, input validation, logging, and error handling in a clean and maintainable way.

The design closely follows how backend trading tools are structured in production environments — separating API access, validation, execution logic, and user interaction into independent components.

---

## Key Capabilities

- Place MARKET and LIMIT orders on Binance Futures Testnet  
- Support for both BUY and SELL sides  
- Command-line based execution using argparse  
- Input validation before sending any request to the exchange  
- Confirmation prompt to prevent accidental orders  
- Structured logging of requests, responses, and errors  
- Clean project structure with separation of concerns  

---

## Technology Stack

- Python 3.10+
- Binance Futures USDT-M Testnet (https://testnet.binancefuture.com)
- [python-binance](https://github.com/sammchardy/python-binance) (community Python SDK; `Client(testnet=True)` for Futures testnet)
- argparse for CLI handling
- python-dotenv for environment variables
- logging module from Python standard library

No paid services, cloud platforms, or billing-based tools are used.

### Futures Testnet REST endpoint

Order placement goes only through `bot.client.create_futures_client`, which passes `testnet=True` to [python-binance](https://github.com/sammchardy/python-binance). The SDK then routes `futures_create_order` to the USDT-M Futures Testnet host, not mainnet:

- **Base:** `https://testnet.binancefuture.com/fapi` (same as `Client.FUTURES_TESTNET_URL` in the SDK)
- **Order path:** `POST …/v1/order` → full URL `https://testnet.binancefuture.com/fapi/v1/order`

At startup, `create_futures_client` checks that the resolved order URL still uses that testnet base. Spot and mainnet futures APIs are not used by this bot.

---

## Project Structure

```
trading-bot/
├── bot/
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   ├── logging_config.py
│   └── cli.py
├── logs/
│   ├── market_order.log
│   └── limit_order.log
├── tests/
│   ├── test_validators.py
│   └── test_client_order_payload.py
├── .env.example
├── SETUP.md
├── requirements.txt
└── run.py
```

---

## Setup Instructions

### 1. Clone the repository

```
git clone <repository-url>
cd <repository-name>/trading-bot
```

All commands below assume your working directory is `trading-bot/` (where `run.py` lives).

For step-by-step API key creation on the Futures Testnet, see [trading-bot/SETUP.md](trading-bot/SETUP.md).

---

### 2. Create and activate a virtual environment

```
python -m venv venv
```

Windows:
```
venv\Scripts\activate
```

Linux / macOS:
```
source venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in `trading-bot/` (copy from `.env.example`). Keys must come from **Binance Futures Testnet** (https://testnet.binancefuture.com), not from mainnet Binance.

| Variable | Required | Description |
|----------|----------|-------------|
| `BINANCE_API_KEY` | Yes | Futures Testnet API key |
| `BINANCE_API_SECRET` | Yes | Futures Testnet API secret |

Example:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

---

## Running the Application

Run from `trading-bot/` with the virtual environment activated. The CLI prints an order summary and prompts for confirmation unless you pass `--yes` (or `-y`).

Binance Futures requires order notional (quantity × price) of at least **100 USDT**. The examples below use quantities that meet that minimum.

### Market Order

```
python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

Skip the confirmation prompt:

```
python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --yes
```

### Limit Order

Limit orders require `--price`:

```
python run.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.04 --price 2500
```

### Expected output

After you confirm with `y`, a successful order prints:

```
Order placed successfully:
  orderId:    ...
  status:     FILLED
  executedQty: ...
  avgPrice:   ...
```

Limit orders may show `status: NEW` until the price is reached. On failure, the CLI prints `Validation error: ...` or `Order failed: ...` to stderr. Request and response details are written to `logs/market_order.log` or `logs/limit_order.log`.

---

## Logging

All activity is logged under the `logs/` directory.

Logs include:

- Order request payloads
- Exchange responses
- Execution status
- Error messages and API failures

---

## Verification

From `trading-bot/`, run focused smoke tests (stdlib `unittest`, no API keys):

```
python -m unittest discover -s tests -v
```

CI runs the same checks on push and pull requests via `.github/workflows/smoke.yml`.

---

## Design Decisions

- No trading strategy logic included
- CLI-based execution similar to real trading systems
- Clear separation of concerns
- Minimal and stable dependencies only

---

## Assumptions

- Futures USDT-M Testnet environment only
- No websocket streaming
- Orders executed manually via CLI
- Focus strictly on execution layer reliability

---

## Notes

This project emphasizes clarity, correctness, and maintainability — key requirements when working with financial systems.
