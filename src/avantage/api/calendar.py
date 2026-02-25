"""Calendar endpoints (earnings and IPO schedules)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class CalendarAPI:
    """Access earnings calendar and IPO calendar endpoints."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    @staticmethod
    def _extract_list(data: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
        """Extract a list of entries from the raw API response."""
        if isinstance(data, dict):
            entries = data.get("data")
            if isinstance(entries, list):
                return entries
            return [data] if data else []
        if isinstance(data, list):
            return data
        return []

    async def earnings(
        self,
        *,
        symbol: str | None = None,
        horizon: str = "3month",
    ) -> list[dict[str, Any]]:
        """Fetch upcoming earnings announcements.

        Args:
            symbol: Optional ticker to filter by.
            horizon: ``"3month"``, ``"6month"``, or ``"12month"``.

        Returns:
            List of earnings calendar entries.
        """
        data = await self._request("EARNINGS_CALENDAR", symbol=symbol, horizon=horizon)
        return self._extract_list(data)

    async def ipo(self) -> list[dict[str, Any]]:
        """Fetch upcoming IPO events.

        Returns:
            List of IPO calendar entries.
        """
        data = await self._request("IPO_CALENDAR")
        return self._extract_list(data)
