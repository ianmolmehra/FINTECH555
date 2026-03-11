# FINTECH555 — API Integration Layer

## Overview
This directory contains stub files for Phase 2 live data integration.
All analytics in Phase 1 run fully offline using uploaded CSV/Excel files.

## Phase 2 Activation Guide

### 1. LLM Explainer (Claude or GPT)
**File:** `llm_explainer_stub.py`

```bash
# Install Anthropic SDK
pip install anthropic

# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"
# Or on Windows: set ANTHROPIC_API_KEY=your-key-here
```

Then in `llm_explainer_stub.py`, uncomment the Claude API block and remove the `return None` line.

**To get an API key:**
- Claude: https://console.anthropic.com/
- GPT: https://platform.openai.com/

### 2. Zerodha Kite Connect API
**File:** `broker_api_stub.py`

```bash
pip install kiteconnect
```

- Register app at: https://kite.trade/
- Generate API key + secret
- Complete login flow to get access_token
- Pass tokens to `fetch_zerodha_trades(api_key, access_token, from_date, to_date)`

### 3. Upstox API v2
**File:** `broker_api_stub.py`

```bash
pip install upstox-python-sdk
```

- Register at: https://upstox.com/developer/
- Generate API key + redirect URI
- Use OAuth flow to get access_token
- Pass to `fetch_upstox_trades(api_key, access_token, from_date, to_date)`

### 4. Market Data (yfinance / NSEPython)
**File:** `market_data_stub.py`

```bash
pip install yfinance nsepython
```

- `fetch_ohlcv_yfinance(symbol, from_date, to_date)` — Yahoo Finance OHLCV
- Use `.NS` suffix for NSE stocks: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`

## Expected Response Format
All broker API functions must return a DataFrame with these standard columns:
```
Stock Symbol | Buy Date | Sell Date | Buy Price | Sell Price | Quantity
```

## Current Status
| Component | Phase 1 (CSV) | Phase 2 (API) |
|-----------|:---:|:---:|
| Trade Data | ✅ Active | 🔧 Stub ready |
| Market Data | ✅ GBM synthetic | 🔧 Stub ready |
| LLM Explain | ✅ Rule engine | 🔧 Stub ready |
