# Setup Guide: API Keys and Running the Project

Step-by-step instructions to create Binance Futures Testnet API keys and run the trading-bot CLI.

---

## Part 1: Create Binance Futures Testnet API Keys

The project uses **Binance Futures Testnet** only. No real money; testnet uses fake USDT.

### Step 1.1: Open the Futures Testnet site

1. In your browser go to: **https://testnet.binancefuture.com**
2. You should see the Binance Futures Testnet login/trading interface.

### Step 1.2: Log in or register

1. Click **Log in** (or **Register** if you don’t have a testnet account).
2. **Register (if needed):**
   - Use an email (can be any valid format; no real verification on testnet).
   - Set a password and complete the form.
   - Log in after registration.
3. **Log in:** Enter your testnet email and password.

### Step 1.3: Open API Management

1. After login, click your **profile/account** (usually top-right: avatar or email).
2. In the menu, choose **API Management** (or **API Key**, depending on the UI).
3. If you don’t see it on the main page, look under **Account** or **Settings** for “API Management” or “API Key”.

### Step 1.4: Create a new API key

1. Click **Create API** or **Generate API Key**.
2. You may be asked to:
   - Enter a **label** (e.g. `trading-bot`) for your reference.
   - Complete a captcha or security check if shown.
3. Click **Create** / **Confirm**.
4. The site will show:
   - **API Key** (long string)
   - **Secret Key** (only shown once)

### Step 1.5: Save the keys safely

1. **Copy the API Key** and paste it somewhere temporary (you’ll put it in `.env` next).
2. **Copy the Secret Key** and paste it somewhere temporary.
3. **Important:** The secret is usually shown only once. If you lose it, you’ll need to create a new API key and disable/delete the old one.
4. Do not share these keys or commit them to git. They are only for your testnet account.

### Step 1.6: (Optional) Restrict the key

If the testnet UI allows:

- You can restrict the key to “Futures” or “Futures Testnet” only.
- You can restrict by IP if you want (optional).

The bot only needs permission to place orders on Futures Testnet.

---

## Part 2: Configure the Project

### Step 2.1: Open the project folder

1. Open a terminal (PowerShell, Command Prompt, or your IDE terminal).
2. Go to the project root (where `run.py` and the `bot` folder are):

   ```bash
   cd d:\Fun\Primetrade\trading-bot
   ```

   Use the actual path where your `trading-bot` folder lives.

### Step 2.2: Create a virtual environment (recommended)

1. Create a venv:

   ```bash
   python -m venv .venv
   ```

2. Activate it:
   - **Windows (PowerShell):**
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```bash
     .venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```
3. Your prompt should start with `(.venv)`.

### Step 2.3: Install dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

You should see `python-binance` (imports as `binance`) and `python-dotenv` installed. The bot uses `Client(testnet=True)` so `futures_create_order` posts to `https://testnet.binancefuture.com/fapi/v1/order` (see `bot/client.py` and the README “Futures Testnet REST endpoint” section).

### Step 2.4: Put your API keys in `.env`

1. Copy `.env.example` to `.env` if you do not already have one.
2. Open `.env` in the project root (same folder as `run.py`).
3. Replace the placeholders with your **Futures Testnet** keys (not mainnet keys):

   ```env
   BINANCE_API_KEY=paste_your_api_key_here
   BINANCE_API_SECRET=paste_your_secret_key_here
   ```

4. Save the file. Do not add quotes unless the key/secret itself contains spaces (usually they don’t).
5. Ensure there are no extra spaces before or after the `=` sign.

---

## Part 3: Run the Project

All commands below are run from the project root: `d:\Fun\Primetrade\trading-bot` (or your path), with the virtual environment activated.

### Step 3.1: Check that the CLI works

```bash
python run.py --help
```

You should see the help text with options: `--symbol`, `--side`, `--type`, `--quantity`, `--price`, `--yes`.

### Step 3.2: Place a market order (example)

1. Run (Binance requires notional ≥ 100 USDT; for BTC, 0.002 is safe):

   ```bash
   python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
   ```

2. The script will print an **order summary** and ask:

   ```text
   Place this order on Binance Futures Testnet? [y/N]
   ```

3. Type **y** and press Enter to place the order, or just Enter to cancel.
4. On success you’ll see something like:

   ```text
   Order placed successfully:
     orderId:    ...
     status:     FILLED
     executedQty: 0.002
     avgPrice:   ...
   ```

### Step 3.3: Skip the confirmation prompt

To place an order without being asked (e.g. for scripts):

```bash
python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --yes
```

Or use the short form: `-y`.

### Step 3.4: Place a limit order (example)

Limit orders require `--price`:

```bash
python run.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 2500
```

Confirm when prompted (or add `--yes` to skip).

### Step 3.5: More examples

- Market sell (notional ≥ 100 USDT):
  ```bash
  python run.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.002
  ```

- Limit buy:
  ```bash
  python run.py --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.05 --price 2400
  ```

### Step 3.6: Where logs are written

- Market orders: `logs/market_order.log`
- Limit orders: `logs/limit_order.log`

Open these files to see request/response and error details (timestamps and log levels).

---

## Part 4: Troubleshooting

| Issue | What to do |
|-------|------------|
| `ModuleNotFoundError: No module named 'binance'` | Activate the venv and run `pip install -r requirements.txt` again. The PyPI package is `python-binance`; Python imports it as `binance`. |
| `BINANCE_API_KEY and BINANCE_API_SECRET must be set` | Edit `.env` in the project root; ensure both variables are set and the file is saved. |
| `Order failed: ...` (API error) | Check the message (e.g. insufficient balance, invalid symbol). On testnet, get free testnet USDT from the testnet site if needed. Check `logs/market_order.log` or `logs/limit_order.log` for full error. |
| `Order's notional must be no smaller than 100` | Binance Futures requires notional (quantity × price) ≥ 100 USDT. Use a larger quantity, e.g. `0.002` for BTCUSDT or `0.03` for ETHUSDT. |
| `Validation error: Price is required for LIMIT orders` | For `--type LIMIT` you must pass `--price` (e.g. `--price 2500`). |
| `Validation error: Quantity must be greater than zero` | Use a positive quantity (e.g. `0.001`). |
| Nothing happens when I type at the prompt | Make sure you’re typing in the same terminal where the script is running; the prompt is “Place this order on Binance Futures Testnet? [y/N]”. |
| `failed to locate pyvenv.cfg` when running `python -m venv venv` | Usually means an existing `venv` folder is broken or incomplete. Either: (1) Close any terminal/IDE using that venv, delete the `venv` folder, then run `python -m venv venv` again; or (2) Create the venv inside `trading-bot` with a different name: `cd trading-bot` then `python -m venv .venv`, and activate with `trading-bot\.venv\Scripts\Activate.ps1`. |

---

## Quick reference

1. **Create API keys:** https://testnet.binancefuture.com → Log in → API Management → Create API → Copy Key and Secret.
2. **Configure:** Put Key and Secret in `.env` as `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
3. **Run:** From project root, with venv activated: `python run.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002` (notional must be ≥ 100 USDT; then confirm with `y` or use `--yes`).
