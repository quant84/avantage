"""Common models used across API domains."""

from __future__ import annotations

from pydantic import BaseModel


class TimeSeriesEntry(BaseModel):
    """Single OHLCV data point."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float | None = None
    dividend_amount: float | None = None
    split_coefficient: float | None = None


class TimeSeriesResponse(BaseModel):
    """Response containing time series data with metadata."""

    metadata: dict[str, str]
    data: list[TimeSeriesEntry]


class DataPoint(BaseModel):
    """Generic date-value pair for economic/commodity data."""

    date: str
    value: float | None
