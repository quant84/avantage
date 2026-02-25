"""Pydantic models for cryptocurrency API responses."""

from __future__ import annotations

from pydantic import BaseModel


class CryptoDataPoint(BaseModel):
    """Single cryptocurrency time series data point."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    market_cap: float | None = None
