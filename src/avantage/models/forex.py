"""Pydantic models for forex API responses."""

from __future__ import annotations

from pydantic import BaseModel


class ExchangeRate(BaseModel):
    """Realtime exchange rate between two currencies."""

    from_currency_code: str
    from_currency_name: str
    to_currency_code: str
    to_currency_name: str
    exchange_rate: float
    last_refreshed: str
    timezone: str
    bid_price: float | None = None
    ask_price: float | None = None


class FXDataPoint(BaseModel):
    """Single forex time series data point."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
