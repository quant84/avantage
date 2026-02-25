"""Pydantic models for options API responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OptionsContract(BaseModel):
    """Single options contract."""

    model_config = ConfigDict(populate_by_name=True)

    contract_id: str = Field(alias="contractID")
    symbol: str
    expiration: str
    strike: float
    type: str
    last: float | None = None
    mark: float | None = None
    bid: float | None = None
    bid_size: int | None = None
    ask: float | None = None
    ask_size: int | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    rho: float | None = None
    in_the_money: bool | None = None


class OptionsChain(BaseModel):
    """Options chain response."""

    symbol: str
    contracts: list[OptionsContract]
