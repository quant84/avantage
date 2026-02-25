"""Pydantic models for equity API responses."""

from __future__ import annotations

from pydantic import BaseModel


class GlobalQuote(BaseModel):
    """Realtime quote for a single symbol."""

    symbol: str
    open: float
    high: float
    low: float
    price: float
    volume: int
    latest_trading_day: str
    previous_close: float
    change: float
    change_percent: str


class BulkQuoteEntry(BaseModel):
    """Single entry from a bulk quote response."""

    symbol: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    price: float | None = None
    volume: int | None = None
    latest_trading_day: str | None = None
    previous_close: float | None = None
    change: float | None = None
    change_percent: str | None = None


class SymbolMatch(BaseModel):
    """Search result from SYMBOL_SEARCH."""

    symbol: str
    name: str
    type: str
    region: str
    market_open: str
    market_close: str
    timezone: str
    currency: str
    match_score: str


class MarketStatus(BaseModel):
    """Market status for a region."""

    market_type: str
    region: str
    primary_exchanges: str
    local_open: str
    local_close: str
    current_status: str
    notes: str
