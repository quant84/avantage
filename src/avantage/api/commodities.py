"""Commodity price endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage.models.commodities import CommodityResponse
from avantage.models.common import DataPoint

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avantage._types import CommodityInterval


class CommoditiesAPI:
    """Access commodity price endpoints (WTI, Brent, natural gas, metals, agriculture)."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helper -------------------------------------------------------

    async def _get(
        self,
        function: str,
        interval: CommodityInterval | None = None,
    ) -> CommodityResponse:
        """Fetch a commodity endpoint and parse the standard response format.

        Args:
            function: Alpha Vantage function name (e.g. ``WTI``).
            interval: Optional time interval (daily, weekly, monthly).

        Returns:
            Parsed commodity response with typed data points.
        """
        raw = await self._request(function, interval=interval)
        data = [
            DataPoint(
                date=entry["date"],
                value=float(entry["value"]) if entry.get("value") not in (None, ".") else None,
            )
            for entry in raw.get("data", [])
        ]
        return CommodityResponse(
            name=raw.get("name", ""),
            interval=raw.get("interval", ""),
            unit=raw.get("unit", ""),
            data=data,
        )

    @staticmethod
    def _parse_commodity_response(raw: dict[str, Any]) -> CommodityResponse:
        """Parse standard commodity response format into a model."""
        data = [
            DataPoint(
                date=entry["date"],
                value=float(entry["value"]) if entry.get("value") not in (None, ".") else None,
            )
            for entry in raw.get("data", [])
        ]
        return CommodityResponse(
            name=raw.get("name", ""),
            interval=raw.get("interval", ""),
            unit=raw.get("unit", ""),
            data=data,
        )

    # -- Public endpoints -----------------------------------------------------

    async def wti(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """West Texas Intermediate crude oil prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("WTI", interval=interval)

    async def brent(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Brent crude oil prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("BRENT", interval=interval)

    async def natural_gas(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Henry Hub natural gas spot prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("NATURAL_GAS", interval=interval)

    async def copper(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global copper prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("COPPER", interval=interval)

    async def aluminum(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global aluminum prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("ALUMINUM", interval=interval)

    async def wheat(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global wheat prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("WHEAT", interval=interval)

    async def corn(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global corn prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("CORN", interval=interval)

    async def cotton(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global cotton prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("COTTON", interval=interval)

    async def sugar(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global sugar prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("SUGAR", interval=interval)

    async def coffee(self, *, interval: CommodityInterval = "monthly") -> CommodityResponse:
        """Global coffee prices.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("COFFEE", interval=interval)

    async def all_commodities(
        self, *, interval: CommodityInterval = "monthly"
    ) -> CommodityResponse:
        """Global price index of all commodities.

        Args:
            interval: Time interval for data points.
        """
        return await self._get("ALL_COMMODITIES", interval=interval)

    async def gold_silver_spot(self, symbol: str) -> dict[str, Any]:
        """Live spot price of gold or silver.

        Args:
            symbol: Metal identifier -- ``"GOLD"`` / ``"XAU"`` for gold,
                ``"SILVER"`` / ``"XAG"`` for silver.

        Returns:
            Raw spot price data for the specified metal.
        """
        return await self._request("GOLD_SILVER_SPOT", symbol=symbol)

    async def gold_silver_history(
        self,
        symbol: str,
        *,
        interval: CommodityInterval = "monthly",
    ) -> CommodityResponse:
        """Historical gold or silver prices.

        Args:
            symbol: Metal identifier -- ``"GOLD"`` / ``"XAU"`` for gold,
                ``"SILVER"`` / ``"XAG"`` for silver.
            interval: Time interval for data points.
        """
        raw = await self._request("GOLD_SILVER_HISTORY", symbol=symbol, interval=interval)
        return self._parse_commodity_response(raw)
