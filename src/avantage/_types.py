"""Shared type aliases and literal types for the avantage package."""

from __future__ import annotations

from typing import Literal

Interval = Literal["1min", "5min", "15min", "30min", "60min"]
"""Intraday time interval for time series and indicator endpoints."""

OutputSize = Literal["compact", "full"]
"""Controls the size of time series data returned (compact=100, full=20+ years)."""

DataType = Literal["json", "csv"]
"""Response format from the API. Internal use only."""

CommodityInterval = Literal["daily", "weekly", "monthly"]
"""Time interval for commodity price endpoints."""

EconomicInterval = Literal["quarterly", "annual"]
"""Time interval for economic indicator endpoints."""

MaturityInterval = Literal["daily", "weekly", "monthly"]
"""Time interval for treasury yield endpoints."""

Maturity = Literal["3month", "2year", "5year", "7year", "10year", "30year"]
"""Treasury bond maturity duration."""

SeriesType = Literal["close", "open", "high", "low"]
"""Price series type used by technical indicator endpoints."""
