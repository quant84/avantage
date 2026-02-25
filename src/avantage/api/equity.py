"""Equity (stock) time series and quote endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import clean_key, parse_float, parse_int
from avantage.models.common import TimeSeriesEntry, TimeSeriesResponse
from avantage.models.equity import (
    BulkQuoteEntry,
    GlobalQuote,
    MarketStatus,
    SymbolMatch,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avantage._types import Interval, OutputSize


class EquityAPI:
    """Access equity time series, quotes, search, and market status endpoints."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helpers ------------------------------------------------------

    @staticmethod
    def _parse_time_series(data: dict[str, Any]) -> TimeSeriesResponse:
        """Parse a generic Alpha Vantage time series response.

        Finds the metadata and time series keys dynamically, then builds
        a :class:`TimeSeriesResponse` from the nested OHLCV data.
        """
        metadata_key = next(
            (k for k in data if "Meta Data" in k),
            None,
        )
        series_key = next(
            (k for k in data if k != metadata_key and ("Time Series" in k or "Stock Quotes" in k)),
            None,
        )

        metadata: dict[str, str] = {}
        if metadata_key:
            metadata = {clean_key(k): v for k, v in data[metadata_key].items()}

        entries: list[TimeSeriesEntry] = []
        if series_key:
            for timestamp, values in data[series_key].items():
                cleaned = {clean_key(k): v for k, v in values.items()}
                entries.append(
                    TimeSeriesEntry(
                        timestamp=timestamp,
                        open=float(cleaned["open"]),
                        high=float(cleaned["high"]),
                        low=float(cleaned["low"]),
                        close=float(cleaned["close"]),
                        volume=int(cleaned["volume"]),
                        adjusted_close=parse_float(cleaned.get("adjusted close")),
                        dividend_amount=parse_float(cleaned.get("dividend amount")),
                        split_coefficient=parse_float(cleaned.get("split coefficient")),
                    )
                )

        return TimeSeriesResponse(metadata=metadata, data=entries)

    # -- Time series endpoints ------------------------------------------------

    async def intraday(
        self,
        symbol: str,
        interval: Interval,
        *,
        adjusted: bool = True,
        extended_hours: bool = True,
        month: str | None = None,
        outputsize: OutputSize = "compact",
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch intraday time series for a symbol.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``).
            interval: Time interval between data points.
            adjusted: Whether to return adjusted prices.
            extended_hours: Include pre/post market data.
            month: Specific month in ``YYYY-MM`` format (premium).
            outputsize: ``"compact"`` (100 points) or ``"full"``.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_INTRADAY",
            symbol=symbol,
            interval=interval,
            adjusted=str(adjusted).lower(),
            extended_hours=str(extended_hours).lower(),
            month=month,
            outputsize=outputsize,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def daily(
        self,
        symbol: str,
        *,
        outputsize: OutputSize = "compact",
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch daily time series for a symbol.

        Args:
            symbol: Ticker symbol.
            outputsize: ``"compact"`` (100 points) or ``"full"`` (20+ years).
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_DAILY",
            symbol=symbol,
            outputsize=outputsize,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def daily_adjusted(
        self,
        symbol: str,
        *,
        outputsize: OutputSize = "compact",
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch daily adjusted time series for a symbol.

        Args:
            symbol: Ticker symbol.
            outputsize: ``"compact"`` (100 points) or ``"full"`` (20+ years).
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_DAILY_ADJUSTED",
            symbol=symbol,
            outputsize=outputsize,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def weekly(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch weekly time series for a symbol.

        Args:
            symbol: Ticker symbol.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_WEEKLY",
            symbol=symbol,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def weekly_adjusted(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch weekly adjusted time series for a symbol.

        Args:
            symbol: Ticker symbol.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_WEEKLY_ADJUSTED",
            symbol=symbol,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def monthly(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch monthly time series for a symbol.

        Args:
            symbol: Ticker symbol.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_MONTHLY",
            symbol=symbol,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    async def monthly_adjusted(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> TimeSeriesResponse:
        """Fetch monthly adjusted time series for a symbol.

        Args:
            symbol: Ticker symbol.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "TIME_SERIES_MONTHLY_ADJUSTED",
            symbol=symbol,
            entitlement=entitlement,
        )
        return self._parse_time_series(data)

    # -- Quote endpoints ------------------------------------------------------

    async def quote(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> GlobalQuote:
        """Fetch the latest realtime quote for a symbol.

        Args:
            symbol: Ticker symbol.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "GLOBAL_QUOTE",
            symbol=symbol,
            entitlement=entitlement,
        )
        raw = data["Global Quote"]
        cleaned = {clean_key(k): v for k, v in raw.items()}
        return GlobalQuote(
            symbol=cleaned["symbol"],
            open=float(cleaned["open"]),
            high=float(cleaned["high"]),
            low=float(cleaned["low"]),
            price=float(cleaned["price"]),
            volume=int(cleaned["volume"]),
            latest_trading_day=cleaned["latest trading day"],
            previous_close=float(cleaned["previous close"]),
            change=float(cleaned["change"]),
            change_percent=cleaned["change percent"],
        )

    async def bulk_quotes(
        self,
        symbol: str,
        *,
        entitlement: str | None = None,
    ) -> list[BulkQuoteEntry]:
        """Fetch bulk quotes for one or more symbols.

        Args:
            symbol: Comma-separated ticker symbols or ``"all"`` for all US-traded.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "REALTIME_BULK_QUOTES",
            symbol=symbol,
            entitlement=entitlement,
        )
        entries: list[BulkQuoteEntry] = []
        for item in data.get("data", []):
            entries.append(
                BulkQuoteEntry(
                    symbol=item.get("symbol", ""),
                    open=parse_float(item.get("open")),
                    high=parse_float(item.get("high")),
                    low=parse_float(item.get("low")),
                    price=parse_float(item.get("price")),
                    volume=parse_int(item.get("volume")),
                    latest_trading_day=item.get("latest_trading_day"),
                    previous_close=parse_float(item.get("previous_close")),
                    change=parse_float(item.get("change")),
                    change_percent=item.get("change_percent"),
                )
            )
        return entries

    # -- Search & market status -----------------------------------------------

    async def search(self, keywords: str) -> list[SymbolMatch]:
        """Search for symbols matching the given keywords.

        Args:
            keywords: Free-text search query (e.g. ``"Apple"`` or ``"AAPL"``).
        """
        data = await self._request("SYMBOL_SEARCH", keywords=keywords)
        results: list[SymbolMatch] = []
        for item in data.get("bestMatches", []):
            cleaned = {clean_key(k): v for k, v in item.items()}
            results.append(
                SymbolMatch(
                    symbol=cleaned["symbol"],
                    name=cleaned["name"],
                    type=cleaned["type"],
                    region=cleaned["region"],
                    market_open=cleaned["marketOpen"],
                    market_close=cleaned["marketClose"],
                    timezone=cleaned["timezone"],
                    currency=cleaned["currency"],
                    match_score=cleaned["matchScore"],
                )
            )
        return results

    async def market_status(self) -> list[MarketStatus]:
        """Fetch current market status for all major global exchanges."""
        data = await self._request("MARKET_STATUS")
        return [
            MarketStatus(
                market_type=item["market_type"],
                region=item["region"],
                primary_exchanges=item["primary_exchanges"],
                local_open=item["local_open"],
                local_close=item["local_close"],
                current_status=item["current_status"],
                notes=item["notes"],
            )
            for item in data.get("markets", [])
        ]
