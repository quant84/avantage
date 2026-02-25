"""Economic indicator endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage.models.common import DataPoint
from avantage.models.economic import EconomicResponse

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class EconomicAPI:
    """Access economic indicator endpoints (GDP, CPI, treasury yield, unemployment, etc.)."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helper -------------------------------------------------------

    async def _get(
        self,
        function: str,
        interval: str | None = None,
        maturity: str | None = None,
    ) -> EconomicResponse:
        """Fetch an economic indicator endpoint and parse the standard response format.

        Args:
            function: Alpha Vantage function name (e.g. ``REAL_GDP``).
            interval: Optional time interval (e.g. ``annual``, ``quarterly``, ``monthly``).
            maturity: Optional maturity period for treasury yield (e.g. ``10year``).

        Returns:
            Parsed economic response with typed data points.
        """
        raw = await self._request(function, interval=interval, maturity=maturity)
        data = [
            DataPoint(
                date=entry["date"],
                value=float(entry["value"]) if entry.get("value") not in (None, ".") else None,
            )
            for entry in raw.get("data", [])
        ]
        return EconomicResponse(
            name=raw.get("name", ""),
            interval=raw.get("interval", ""),
            unit=raw.get("unit", ""),
            data=data,
        )

    # -- Public endpoints -----------------------------------------------------

    async def real_gdp(self, *, interval: str = "annual") -> EconomicResponse:
        """U.S. Real Gross Domestic Product.

        Args:
            interval: ``"annual"`` or ``"quarterly"``.
        """
        return await self._get("REAL_GDP", interval=interval)

    async def real_gdp_per_capita(self) -> EconomicResponse:
        """U.S. Real GDP per capita (quarterly)."""
        return await self._get("REAL_GDP_PER_CAPITA")

    async def treasury_yield(
        self,
        *,
        interval: str = "monthly",
        maturity: str = "10year",
    ) -> EconomicResponse:
        """U.S. Treasury bond yield.

        Args:
            interval: ``"daily"``, ``"weekly"``, or ``"monthly"``.
            maturity: ``"3month"``, ``"2year"``, ``"5year"``, ``"7year"``,
                ``"10year"``, or ``"30year"``.
        """
        return await self._get("TREASURY_YIELD", interval=interval, maturity=maturity)

    async def federal_funds_rate(self, *, interval: str = "monthly") -> EconomicResponse:
        """U.S. Federal Funds effective interest rate.

        Args:
            interval: ``"daily"``, ``"weekly"``, or ``"monthly"``.
        """
        return await self._get("FEDERAL_FUNDS_RATE", interval=interval)

    async def cpi(self, *, interval: str = "monthly") -> EconomicResponse:
        """U.S. Consumer Price Index.

        Args:
            interval: ``"monthly"`` or ``"semiannual"``.
        """
        return await self._get("CPI", interval=interval)

    async def inflation(self) -> EconomicResponse:
        """U.S. annual inflation rate."""
        return await self._get("INFLATION")

    async def retail_sales(self) -> EconomicResponse:
        """U.S. monthly Advance Retail Sales."""
        return await self._get("RETAIL_SALES")

    async def durables(self) -> EconomicResponse:
        """U.S. monthly manufacturers' new orders for durable goods."""
        return await self._get("DURABLES")

    async def unemployment(self) -> EconomicResponse:
        """U.S. monthly unemployment rate."""
        return await self._get("UNEMPLOYMENT")

    async def nonfarm_payroll(self) -> EconomicResponse:
        """U.S. monthly total nonfarm payroll."""
        return await self._get("NONFARM_PAYROLL")
