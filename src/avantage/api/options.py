"""Options chain endpoints (realtime and historical)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import parse_float, parse_int
from avantage.models.options import OptionsChain, OptionsContract

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class OptionsAPI:
    """Access realtime and historical options chain data."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helpers ------------------------------------------------------

    @staticmethod
    def _parse_chain(symbol: str, data: dict[str, Any]) -> OptionsChain:
        """Parse an options chain response into an :class:`OptionsChain`."""
        contracts: list[OptionsContract] = []
        for item in data.get("data", []):
            contracts.append(
                OptionsContract(
                    contract_id=item["contractID"],
                    symbol=item["symbol"],
                    expiration=item["expiration"],
                    strike=float(item["strike"]),
                    type=item["type"],
                    last=parse_float(item.get("last")),
                    mark=parse_float(item.get("mark")),
                    bid=parse_float(item.get("bid")),
                    bid_size=parse_int(item.get("bid_size")),
                    ask=parse_float(item.get("ask")),
                    ask_size=parse_int(item.get("ask_size")),
                    volume=parse_int(item.get("volume")),
                    open_interest=parse_int(item.get("open_interest")),
                    implied_volatility=parse_float(item.get("implied_volatility")),
                    delta=parse_float(item.get("delta")),
                    gamma=parse_float(item.get("gamma")),
                    theta=parse_float(item.get("theta")),
                    vega=parse_float(item.get("vega")),
                    rho=parse_float(item.get("rho")),
                    in_the_money=_parse_bool(item.get("in_the_money")),
                )
            )
        return OptionsChain(symbol=symbol, contracts=contracts)

    # -- Endpoints ------------------------------------------------------------

    async def chain(
        self,
        symbol: str,
        *,
        require_greeks: bool | None = None,
        contract: str | None = None,
        entitlement: str | None = None,
    ) -> OptionsChain:
        """Fetch the realtime options chain for a symbol.

        Args:
            symbol: Underlying ticker symbol (e.g. ``"AAPL"``).
            require_greeks: Set to ``True`` to include Greeks and implied
                volatility fields in the response. Defaults to ``False``.
            contract: Specific contract ID to filter by.
            entitlement: Premium entitlement flag (``"delayed"`` or ``"realtime"``).
        """
        # Convert bool to API string representation.
        greeks_str: str | None = None
        if require_greeks is not None:
            greeks_str = "true" if require_greeks else "false"

        data = await self._request(
            "REALTIME_OPTIONS",
            symbol=symbol,
            require_greeks=greeks_str,
            contract=contract,
            entitlement=entitlement,
        )
        return self._parse_chain(symbol, data)

    async def historical(
        self,
        symbol: str,
        *,
        date: str | None = None,
        entitlement: str | None = None,
    ) -> OptionsChain:
        """Fetch historical options chain data for a symbol.

        Args:
            symbol: Underlying ticker symbol.
            date: Historical date in ``YYYY-MM-DD`` format.
            entitlement: Premium entitlement flag.
        """
        data = await self._request(
            "HISTORICAL_OPTIONS",
            symbol=symbol,
            date=date,
            entitlement=entitlement,
        )
        return self._parse_chain(symbol, data)


def _parse_bool(value: Any) -> bool | None:
    """Parse a boolean-like value from the API response."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1")
    return bool(value)
