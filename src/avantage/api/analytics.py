"""Advanced analytics endpoints (fixed-window and sliding-window)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class AnalyticsAPI:
    """Access fixed-window and sliding-window analytics endpoints."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    async def fixed_window(
        self,
        symbols: str,
        range: str,
        interval: str,
        calculations: str,
        *,
        ohlc: str = "close",
    ) -> dict[str, Any]:
        """Run fixed-window analytics over a date range.

        Args:
            symbols: Comma-separated ticker symbols (e.g. ``"AAPL,MSFT"``).
                Free keys support up to 5 symbols, premium keys up to 50.
            range: Date range string (e.g. ``"2024-01-01,2024-12-31"``).
            interval: Time interval -- ``"1min"``, ``"5min"``, ``"15min"``,
                ``"30min"``, ``"60min"``, ``"DAILY"``, ``"WEEKLY"``, or
                ``"MONTHLY"``.
            calculations: Comma-separated metric names (e.g. ``"MEAN,STDDEV"``).
            ohlc: Price type to analyse (``"open"``, ``"high"``, ``"low"``,
                ``"close"``).

        Returns:
            Raw analytics response dict.
        """
        return await self._request(
            "ANALYTICS_FIXED_WINDOW",
            SYMBOLS=symbols,
            RANGE=range,
            INTERVAL=interval,
            CALCULATIONS=calculations,
            OHLC=ohlc,
        )

    async def sliding_window(
        self,
        symbols: str,
        range: str,
        interval: str,
        window_size: int,
        calculations: str,
        *,
        ohlc: str = "close",
    ) -> dict[str, Any]:
        """Run sliding-window analytics over a date range.

        Args:
            symbols: Comma-separated ticker symbols (e.g. ``"AAPL,MSFT"``).
                Free keys support up to 5 symbols, premium keys up to 50.
            range: Date range string (e.g. ``"2024-01-01,2024-12-31"``).
            interval: Time interval -- ``"1min"``, ``"5min"``, ``"15min"``,
                ``"30min"``, ``"60min"``, ``"DAILY"``, ``"WEEKLY"``, or
                ``"MONTHLY"``.
            window_size: Size of moving window (minimum 10). Larger values
                are recommended for statistical significance.
            calculations: Comma-separated metric names (e.g. ``"MEAN,STDDEV"``).
                Free keys support 1 metric, premium keys support multiple.
            ohlc: Price type to analyse (``"open"``, ``"high"``, ``"low"``,
                ``"close"``).

        Returns:
            Raw analytics response dict.
        """
        return await self._request(
            "ANALYTICS_SLIDING_WINDOW",
            SYMBOLS=symbols,
            RANGE=range,
            INTERVAL=interval,
            WINDOW_SIZE=window_size,
            CALCULATIONS=calculations,
            OHLC=ohlc,
        )
