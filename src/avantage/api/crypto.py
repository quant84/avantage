"""Cryptocurrency API endpoints."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from avantage._parsers import clean_key, parse_float
from avantage.models.crypto import CryptoDataPoint
from avantage.models.forex import ExchangeRate

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avantage._types import Interval, OutputSize

# Matches keys like "1a. open (USD)" -> captures "open"
_MARKET_KEY_RE = re.compile(r"^\d+[ab]?\.\s*(.+?)(?:\s*\(.+\))?$")


def _parse_exchange_rate(data: dict[str, Any]) -> ExchangeRate:
    """Parse the ``Realtime Currency Exchange Rate`` response."""
    raw = data["Realtime Currency Exchange Rate"]
    cleaned = {clean_key(k): v for k, v in raw.items()}
    return ExchangeRate(
        from_currency_code=cleaned["From_Currency Code"],
        from_currency_name=cleaned["From_Currency Name"],
        to_currency_code=cleaned["To_Currency Code"],
        to_currency_name=cleaned["To_Currency Name"],
        exchange_rate=float(cleaned["Exchange Rate"]),
        last_refreshed=cleaned["Last Refreshed"],
        timezone=cleaned["Time Zone"],
        bid_price=parse_float(cleaned.get("Bid Price")),
        ask_price=parse_float(cleaned.get("Ask Price")),
    )


def _normalize_crypto_key(key: str) -> str:
    """Normalize a crypto response key to a simple field name.

    Handles both standard keys (``"1. open"``) and market-specific keys
    (``"1a. open (USD)"``).  Returns a lowercase identifier such as
    ``"open"``, ``"high"``, ``"volume"``, or ``"market cap"``.
    """
    m = _MARKET_KEY_RE.match(key)
    if m:
        return m.group(1).strip().lower()
    return clean_key(key).lower()


def _parse_crypto_series(
    data: dict[str, Any],
    market: str | None = None,
) -> list[CryptoDataPoint]:
    """Parse any crypto time series response into a list of data points.

    For intraday, keys use the standard numbered format (``"1. open"``).
    For daily/weekly/monthly, keys include a market suffix
    (``"1a. open (USD)"``).  We use only the ``a``-variant values for
    OHLC when both ``a`` and ``b`` variants exist.

    Args:
        data: Raw API response dict.
        market: Market currency (e.g. ``"USD"``).  Used for documentation
            only; parsing is driven by key structure.
    """
    ts_key = next((k for k in data if "Time Series" in k), None)
    if ts_key is None:
        return []

    series: dict[str, dict[str, str]] = data[ts_key]
    points: list[CryptoDataPoint] = []

    for timestamp, values in series.items():
        # Determine if this is the market-specific format by checking for "a." keys.
        has_market_keys = any("a." in k or "b." in k for k in values)

        if has_market_keys:
            # Daily/weekly/monthly format: prefer "a" variant, skip "b" duplicates.
            filtered = {k: v for k, v in values.items() if "b." not in k}
            normalized = {_normalize_crypto_key(k): v for k, v in filtered.items()}
        else:
            # Intraday standard format.
            normalized = {clean_key(k).lower(): v for k, v in values.items()}

        points.append(
            CryptoDataPoint(
                timestamp=timestamp,
                open=float(normalized["open"]),
                high=float(normalized["high"]),
                low=float(normalized["low"]),
                close=float(normalized["close"]),
                volume=parse_float(normalized.get("volume")),
                market_cap=parse_float(normalized.get("market cap")),
            )
        )
    return points


class CryptoAPI:
    """Cryptocurrency endpoints.

    Provides access to realtime crypto exchange rates and time series
    (intraday, daily, weekly, monthly).
    """

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    async def exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRate:
        """Get the realtime exchange rate for a cryptocurrency pair.

        Args:
            from_currency: Source currency code (e.g. ``"BTC"``).
            to_currency: Target currency code (e.g. ``"USD"``).
        """
        data = await self._request(
            "CURRENCY_EXCHANGE_RATE",
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return _parse_exchange_rate(data)

    async def intraday(
        self,
        symbol: str,
        market: str,
        interval: Interval,
        *,
        outputsize: OutputSize = "compact",
    ) -> list[CryptoDataPoint]:
        """Get intraday crypto time series.

        Args:
            symbol: Crypto symbol (e.g. ``"BTC"``).
            market: Market currency (e.g. ``"USD"``).
            interval: Time interval between data points.
            outputsize: ``"compact"`` (100 points) or ``"full"`` (complete history).
        """
        data = await self._request(
            "CRYPTO_INTRADAY",
            symbol=symbol,
            market=market,
            interval=interval,
            outputsize=outputsize,
        )
        return _parse_crypto_series(data)

    async def daily(
        self,
        symbol: str,
        market: str,
    ) -> list[CryptoDataPoint]:
        """Get daily crypto time series.

        Args:
            symbol: Crypto symbol (e.g. ``"BTC"``).
            market: Market currency (e.g. ``"USD"``).
        """
        data = await self._request(
            "DIGITAL_CURRENCY_DAILY",
            symbol=symbol,
            market=market,
        )
        return _parse_crypto_series(data, market=market)

    async def weekly(
        self,
        symbol: str,
        market: str,
    ) -> list[CryptoDataPoint]:
        """Get weekly crypto time series.

        Args:
            symbol: Crypto symbol (e.g. ``"BTC"``).
            market: Market currency (e.g. ``"USD"``).
        """
        data = await self._request(
            "DIGITAL_CURRENCY_WEEKLY",
            symbol=symbol,
            market=market,
        )
        return _parse_crypto_series(data, market=market)

    async def monthly(
        self,
        symbol: str,
        market: str,
    ) -> list[CryptoDataPoint]:
        """Get monthly crypto time series.

        Args:
            symbol: Crypto symbol (e.g. ``"BTC"``).
            market: Market currency (e.g. ``"USD"``).
        """
        data = await self._request(
            "DIGITAL_CURRENCY_MONTHLY",
            symbol=symbol,
            market=market,
        )
        return _parse_crypto_series(data, market=market)
