"""Pydantic models for technical indicator responses."""

from __future__ import annotations

from pydantic import BaseModel


class IndicatorValue(BaseModel):
    """Single indicator data point."""

    timestamp: str
    values: dict[str, float | None]


class IndicatorResponse(BaseModel):
    """Response from a technical indicator endpoint."""

    metadata: dict[str, str]
    data: list[IndicatorValue]
