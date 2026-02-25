"""Pydantic models for commodity API responses."""

from __future__ import annotations

from pydantic import BaseModel

from avantage.models.common import DataPoint  # noqa: TC001 -- Pydantic needs runtime access


class CommodityResponse(BaseModel):
    """Response containing commodity price data."""

    name: str
    interval: str
    unit: str
    data: list[DataPoint]
