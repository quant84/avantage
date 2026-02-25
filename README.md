# avantage

[![CI](https://github.com/quant84/avantage/actions/workflows/ci.yml/badge.svg)](https://github.com/quant84/avantage/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/avantage)](https://pypi.org/project/avantage/)
[![Python](https://img.shields.io/pypi/pyversions/avantage)](https://pypi.org/project/avantage/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Modern, fully-typed Python wrapper for the [Alpha Vantage](https://www.alphavantage.co/) API.

- **Async-first** -- built on `httpx` for native async/await support
- **Fully typed** -- every parameter and return value has type annotations; passes `mypy --strict`
- **110+ endpoints** -- stocks, forex, crypto, commodities, fundamentals, economic indicators, 50+ technical indicators, options, news sentiment, and more
- **Pydantic v2 models** -- all responses parsed into typed dataclasses, not raw dicts
- **Built-in resilience** -- token-bucket rate limiting, retry with exponential backoff + jitter
- **Minimal dependencies** -- just `httpx` and `pydantic`

## Installation

```bash
pip install avantage
```

With optional pandas support:

```bash
pip install avantage[pandas]
```

## Quick Start

```python
import asyncio
from avantage import AlphaVantageClient

async def main():
    async with AlphaVantageClient("YOUR_API_KEY") as client:
        # Get a stock quote
        quote = await client.equity.quote("AAPL")
        print(f"{quote.symbol}: ${quote.price} ({quote.change_percent})")

        # Get daily time series
        series = await client.equity.daily("MSFT")
        for entry in series.data[:3]:
            print(f"  {entry.timestamp}: O={entry.open} H={entry.high} L={entry.low} C={entry.close}")

        # Technical indicators
        rsi = await client.indicators.rsi("AAPL", "daily", time_period=14, series_type="close")
        print(f"RSI: {rsi.data[0].values}")

asyncio.run(main())
```

You can also set your API key via the environment variable `ALPHAVANTAGE_API_KEY`:

```python
import os
os.environ["ALPHAVANTAGE_API_KEY"] = "YOUR_KEY"

client = AlphaVantageClient(os.environ["ALPHAVANTAGE_API_KEY"])
```

## Plotting

Responses are Pydantic models, so you'll need to convert them to pandas DataFrames for plotting. Install the extras:

```bash
pip install avantage[pandas] matplotlib
```

### Intraday Time Series

```python
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from avantage import AlphaVantageClient

async def main():
    async with AlphaVantageClient("YOUR_API_KEY") as client:
        series = await client.equity.intraday("IBM", "5min")

    df = pd.DataFrame([
        {"time": e.timestamp, "close": e.close} for e in series.data
    ])
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    df.plot(x="time", y="close", title="IBM Intraday Close Price (5-min)", legend=False)
    plt.ylabel("Price (USD)")
    plt.tight_layout()
    plt.show()

asyncio.run(main())
```

![IBM Intraday](https://raw.githubusercontent.com/quant84/avantage/main/images/intraday.png)

### Bollinger Bands

```python
async def main():
    async with AlphaVantageClient("YOUR_API_KEY") as client:
        bbands = await client.indicators.bbands("IBM", "daily", time_period=20, series_type="close")

    df = pd.DataFrame([
        {
            "date": e.timestamp,
            "upper": e.values["Real Upper Band"],
            "middle": e.values["Real Middle Band"],
            "lower": e.values["Real Lower Band"],
        }
        for e in bbands.data
    ])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").tail(90)

    fig, ax = plt.subplots()
    ax.plot(df["date"], df["upper"], label="Upper Band")
    ax.plot(df["date"], df["middle"], label="Middle Band (SMA 20)")
    ax.plot(df["date"], df["lower"], label="Lower Band")
    ax.fill_between(df["date"], df["upper"], df["lower"], alpha=0.1)
    ax.set_title("IBM Bollinger Bands (Daily)")
    ax.legend()
    plt.tight_layout()
    plt.show()

asyncio.run(main())
```

![IBM Bollinger Bands](https://raw.githubusercontent.com/quant84/avantage/main/images/bollinger_bands.png)

### Crypto Daily

```python
async def main():
    async with AlphaVantageClient("YOUR_API_KEY") as client:
        crypto = await client.crypto.daily("BTC", "USD")

    df = pd.DataFrame([
        {"date": e.timestamp, "close": e.close} for e in crypto.data
    ])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").tail(90)

    df.plot(x="date", y="close", title="Bitcoin Daily Close Price (BTC/USD)", legend=False)
    plt.ylabel("Price (USD)")
    plt.tight_layout()
    plt.show()

asyncio.run(main())
```

![BTC/USD Daily](https://raw.githubusercontent.com/quant84/avantage/main/images/crypto_daily.png)

## API Reference

The client exposes domain-specific API groups as attributes:

```python
async with AlphaVantageClient(api_key) as client:
    client.equity          # Stocks: quotes, time series, search, market status
    client.forex           # Foreign exchange rates and time series
    client.crypto          # Cryptocurrency rates and time series
    client.commodities     # Oil, gas, metals, agriculture prices
    client.fundamentals    # Company financials, earnings, dividends, splits
    client.economic        # GDP, CPI, unemployment, treasury yields
    client.indicators      # 50+ technical indicators (SMA, RSI, MACD, ...)
    client.intelligence    # News sentiment, top movers, insider transactions
    client.options         # Realtime and historical options chains
    client.analytics       # Fixed and sliding window analytics
    client.calendar        # Earnings and IPO calendars
```

### Equity

```python
# Realtime quote
quote = await client.equity.quote("AAPL")
# quote.symbol, quote.price, quote.change, quote.change_percent, quote.volume

# Time series (intraday, daily, weekly, monthly -- with adjusted variants)
series = await client.equity.daily("AAPL", outputsize="full")
series = await client.equity.intraday("AAPL", "5min")
series = await client.equity.weekly_adjusted("AAPL")

# Search
matches = await client.equity.search("Apple")
# [SymbolMatch(symbol="AAPL", name="Apple Inc", ...)]

# Bulk quotes (up to 100 symbols)
quotes = await client.equity.bulk_quotes("AAPL,MSFT,GOOGL")

# Market status
markets = await client.equity.market_status()
```

### Forex

```python
rate = await client.forex.exchange_rate("USD", "EUR")
# rate.exchange_rate, rate.bid_price, rate.ask_price

series = await client.forex.daily("USD", "EUR")
# [FXDataPoint(timestamp="2024-01-02", open=0.85, high=0.86, low=0.84, close=0.855)]
```

### Crypto

```python
rate = await client.crypto.exchange_rate("BTC", "USD")

daily = await client.crypto.daily("BTC", "USD")
# [CryptoDataPoint(timestamp=..., open=..., volume=..., market_cap=...)]
```

### Commodities

```python
oil = await client.commodities.wti(interval="daily")
# CommodityResponse(name="WTI", interval="daily", unit="dollars per barrel", data=[...])

gas = await client.commodities.natural_gas()
copper = await client.commodities.copper()

# Precious metals
gold_spot = await client.commodities.gold_silver_spot("GOLD")
gold_history = await client.commodities.gold_silver_history("GOLD", interval="daily")
```

### Fundamentals

```python
overview = await client.fundamentals.overview("AAPL")
# overview.market_capitalization, overview.pe_ratio, overview.eps, overview.beta, ...

income = await client.fundamentals.income_statement("AAPL")
# income.annual_reports, income.quarterly_reports

earnings = await client.fundamentals.earnings("AAPL")
estimates = await client.fundamentals.earnings_estimates("AAPL")
dividends = await client.fundamentals.dividends("AAPL")
splits = await client.fundamentals.splits("AAPL")
```

### Economic Indicators

```python
gdp = await client.economic.real_gdp(interval="quarterly")
cpi = await client.economic.cpi()
unemployment = await client.economic.unemployment()
yields = await client.economic.treasury_yield(maturity="10year")
```

### Technical Indicators

All 50+ Alpha Vantage indicators are supported:

```python
sma = await client.indicators.sma("AAPL", "daily", time_period=20, series_type="close")
rsi = await client.indicators.rsi("AAPL", "daily", time_period=14, series_type="close")
macd = await client.indicators.macd("AAPL", "daily", series_type="close")
bbands = await client.indicators.bbands("AAPL", "daily", time_period=20, series_type="close")
stoch = await client.indicators.stoch("AAPL", "daily")
adx = await client.indicators.adx("AAPL", "daily", time_period=14)
obv = await client.indicators.obv("AAPL", "daily")
# ... and 40+ more
```

All indicators return `IndicatorResponse` with `metadata` and `data`:

```python
result = await client.indicators.macd("AAPL", "daily", series_type="close")
for point in result.data[:3]:
    print(point.timestamp, point.values)
    # 2024-01-02 {"MACD": 1.23, "MACD_Signal": 0.98, "MACD_Hist": 0.25}
```

### Options

```python
chain = await client.options.chain("AAPL", require_greeks=True)
for contract in chain.contracts[:3]:
    print(f"{contract.type} {contract.strike} exp:{contract.expiration} delta:{contract.delta}")

historical = await client.options.historical("AAPL", date="2024-01-19")
```

### Intelligence

```python
news = await client.intelligence.news_sentiment(tickers="AAPL", limit=10)
for article in news:
    print(f"{article.title} ({article.overall_sentiment_label})")

movers = await client.intelligence.top_movers()
# movers.top_gainers, movers.top_losers, movers.most_actively_traded
```

## Configuration

```python
client = AlphaVantageClient(
    api_key="YOUR_KEY",
    timeout=30.0,            # HTTP timeout in seconds (default: 30)
    max_retries=3,           # Retry attempts on transient failures (default: 3)
    retry_base_delay=1.0,    # Base delay for exponential backoff (default: 1.0)
    retry_max_delay=30.0,    # Maximum backoff delay (default: 30.0)
    rate_limit=75,           # Requests per minute (default: 75, safe for free tier)
)
```

### Rate Limiting

The built-in token-bucket rate limiter prevents exceeding your API quota. The default of 75 requests/minute is safe for the free tier. Premium users can increase this:

```python
client = AlphaVantageClient("YOUR_KEY", rate_limit=600)  # premium: 600/min
```

### Retry Behavior

Transient failures (HTTP 5xx, 429, connection errors, timeouts) are automatically retried with exponential backoff and full jitter. Client errors (4xx) and business logic errors (invalid symbol, bad API key) are never retried.

## Error Handling

```python
from avantage import (
    AlphaVantageError,    # Base exception
    AuthenticationError,  # Invalid API key
    RateLimitError,       # API rate limit exceeded
    SymbolNotFoundError,  # Unknown symbol
    InvalidParameterError,# Bad request parameters
    APIResponseError,     # Malformed response
    UpstreamError,        # Server/network failures
)

try:
    quote = await client.equity.quote("INVALID")
except SymbolNotFoundError:
    print("Symbol not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except AlphaVantageError as e:
    print(f"API error: {e.message}")
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Requirements

- Python 3.11+
- [httpx](https://www.python-httpx.org/) >= 0.28
- [pydantic](https://docs.pydantic.dev/) >= 2.10

## License

MIT
