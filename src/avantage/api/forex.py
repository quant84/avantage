"""Forex (foreign exchange) API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import clean_key, parse_float
from avantage.models.forex import ExchangeRate, FXDataPoint

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avantage._types import Interval, OutputSize


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


def _parse_fx_series(data: dict[str, Any]) -> list[FXDataPoint]:
    """Parse any FX time series response into a list of data points.

    The time series key varies across endpoints (e.g.
    ``Time Series FX (Daily)``, ``Time Series FX (Intraday)``),
    so we locate the first key containing ``"Time Series"``.
    """
    ts_key = next((k for k in data if "Time Series" in k), None)
    if ts_key is None:
        return []

    series: dict[str, dict[str, str]] = data[ts_key]
    points: list[FXDataPoint] = []
    for timestamp, values in series.items():
        cleaned = {clean_key(k): v for k, v in values.items()}
        points.append(
            FXDataPoint(
                timestamp=timestamp,
                open=float(cleaned["open"]),
                high=float(cleaned["high"]),
                low=float(cleaned["low"]),
                close=float(cleaned["close"]),
            )
        )
    return points


class ForexAPI:
    """Foreign exchange rate endpoints.

    Provides access to realtime exchange rates and FX time series
    (intraday, daily, weekly, monthly).
    """

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    async def exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRate:
        """Get the realtime exchange rate between two currencies.

        Args:
            from_currency: Source currency code (e.g. ``"USD"``).
            to_currency: Target currency code (e.g. ``"EUR"``).
        """
        data = await self._request(
            "CURRENCY_EXCHANGE_RATE",
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return _parse_exchange_rate(data)

    async def intraday(
        self,
        from_symbol: str,
        to_symbol: str,
        interval: Interval,
        *,
        outputsize: OutputSize = "compact",
    ) -> list[FXDataPoint]:
        """Get intraday FX time series.

        Args:
            from_symbol: Source currency code (e.g. ``"EUR"``).
            to_symbol: Target currency code (e.g. ``"USD"``).
            interval: Time interval between data points.
            outputsize: ``"compact"`` (100 points) or ``"full"`` (complete history).
        """
        data = await self._request(
            "FX_INTRADAY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            interval=interval,
            outputsize=outputsize,
        )
        return _parse_fx_series(data)

    async def daily(
        self,
        from_symbol: str,
        to_symbol: str,
        *,
        outputsize: OutputSize = "compact",
    ) -> list[FXDataPoint]:
        """Get daily FX time series.

        Args:
            from_symbol: Source currency code (e.g. ``"EUR"``).
            to_symbol: Target currency code (e.g. ``"USD"``).
            outputsize: ``"compact"`` (100 points) or ``"full"`` (complete history).
        """
        data = await self._request(
            "FX_DAILY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            outputsize=outputsize,
        )
        return _parse_fx_series(data)

    async def weekly(
        self,
        from_symbol: str,
        to_symbol: str,
    ) -> list[FXDataPoint]:
        """Get weekly FX time series.

        Args:
            from_symbol: Source currency code (e.g. ``"EUR"``).
            to_symbol: Target currency code (e.g. ``"USD"``).
        """
        data = await self._request(
            "FX_WEEKLY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
        )
        return _parse_fx_series(data)

    async def monthly(
        self,
        from_symbol: str,
        to_symbol: str,
    ) -> list[FXDataPoint]:
        """Get monthly FX time series.

        Args:
            from_symbol: Source currency code (e.g. ``"EUR"``).
            to_symbol: Target currency code (e.g. ``"USD"``).
        """
        data = await self._request(
            "FX_MONTHLY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
        )
        return _parse_fx_series(data)
