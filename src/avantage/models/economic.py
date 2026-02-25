"""Pydantic models for economic indicator API responses."""

from __future__ import annotations

from pydantic import BaseModel

from avantage.models.common import DataPoint  # noqa: TC001 -- Pydantic needs runtime access


class EconomicResponse(BaseModel):
    """Response containing economic indicator data."""

    name: str
    interval: str
    unit: str
    data: list[DataPoint]
