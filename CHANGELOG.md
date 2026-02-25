# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-25

### Added
- `AlphaVantageClient` -- async-first client with rate limiting, retry with backoff, and typed error handling
- Equity API -- 11 endpoints (intraday, daily, weekly, monthly, adjusted variants, quote, bulk quotes, search, market status)
- Forex API -- 5 endpoints (exchange rate, intraday, daily, weekly, monthly)
- Crypto API -- 5 endpoints (exchange rate, intraday, daily, weekly, monthly)
- Commodities API -- 13 endpoints (WTI, Brent, natural gas, copper, aluminum, wheat, corn, cotton, sugar, coffee, all commodities, gold/silver spot, gold/silver history)
- Economic API -- 10 endpoints (GDP, CPI, inflation, unemployment, treasury yield, fed funds rate, retail sales, durables, nonfarm payroll)
- Fundamentals API -- 12 endpoints (overview, ETF profile, income statement, balance sheet, cash flow, earnings, earnings estimates, dividends, splits, listing status, earnings calendar, IPO calendar)
- Technical Indicators API -- 53 indicators (SMA, EMA, RSI, MACD, BBANDS, STOCH, ADX, and more)
- Intelligence API -- 4 endpoints (news sentiment, top movers, earnings call transcript, insider transactions)
- Options API -- 2 endpoints (realtime chain, historical chain)
- Analytics API -- 2 endpoints (fixed window, sliding window)
- Calendar API -- 2 endpoints (earnings, IPO)
- Pydantic v2 models for all response types
- Token-bucket rate limiter with FIFO semaphore gate (concurrency-safe)
- Exponential backoff with full jitter on transient failures
- Typed exception hierarchy (`AuthenticationError`, `RateLimitError`, `SymbolNotFoundError`, etc.)
- Full test suite (110 tests)
- GitHub Actions CI (Python 3.11-3.13)
- Automated PyPI publishing via Trusted Publishers
