"""Calendar endpoints (earnings and IPO schedules)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class CalendarAPI:
    """Access earnings calendar and IPO calendar endpoints."""

    def __init__(
        self,
        request: Callable[..., Awaitable[dict[str, Any]]],
        request_csv: Callable[..., Awaitable[list[dict[str, str]]]] | None = None,
    ) -> None:
        self._request = request
        self._request_csv = request_csv

    async def earnings(
        self,
        *,
        symbol: str | None = None,
        horizon: str = "3month",
    ) -> list[dict[str, str]]:
        """Fetch upcoming earnings announcements.

        Args:
            symbol: Optional ticker to filter by.
            horizon: ``"3month"``, ``"6month"``, or ``"12month"``.

        Returns:
            List of earnings calendar entries (CSV-parsed dicts).
        """
        if self._request_csv is not None:
            return await self._request_csv(
                "EARNINGS_CALENDAR",
                symbol=symbol,
                horizon=horizon,
            )
        data = await self._request("EARNINGS_CALENDAR", symbol=symbol, horizon=horizon)
        return data if isinstance(data, list) else []

    async def ipo(self) -> list[dict[str, str]]:
        """Fetch upcoming IPO events.

        Returns:
            List of IPO calendar entries (CSV-parsed dicts).
        """
        if self._request_csv is not None:
            return await self._request_csv("IPO_CALENDAR")
        data = await self._request("IPO_CALENDAR")
        return data if isinstance(data, list) else []
