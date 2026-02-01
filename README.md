
# Binance Futures Testnet Trading Bot

## Overview

This project is a simplified command-line trading utility built using Python for the Binance Futures USDT-M Testnet.

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
- Binance Futures USDT-M Testnet
- python-binance (official, actively maintained SDK)
- argparse for CLI handling
- python-dotenv for environment variables
- logging module from Python standard library

No paid services, cloud platforms, or billing-based tools are used.

---

## Project Structure

```
trading-bot/
│
├── bot/
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   ├── logging_config.py
│   └── cli.py
│
├── logs/
│   ├── market_order.log
│   └── limit_order.log
│
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```
git clone <repository-url>
cd trading-bot
```

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

Create a `.env` file in the project root:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

---

## Running the Application

### Market Order

```
python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Order

```
python run.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

---

## Logging

All activity is logged under the `logs/` directory.

Logs include:

- Order request payloads
- Exchange responses
- Execution status
- Error messages and API failures

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
