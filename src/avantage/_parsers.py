"""Internal response parsing utilities for Alpha Vantage's quirky formats."""

from __future__ import annotations

import re
from datetime import date, datetime

_PREFIX_RE = re.compile(r"^\d+\.\s*")


def clean_key(key: str) -> str:
    """Strip numbered prefixes from Alpha Vantage keys.

    Examples:
        >>> clean_key("1. open")
        'open'
        >>> clean_key("5. volume")
        'volume'
    """
    return _PREFIX_RE.sub("", key).strip()


def parse_float(value: str | float | int | None) -> float | None:
    """Safely parse a value to float, returning None for missing/invalid values."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = value.strip()
    if value in ("", "None", "-", "."):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_int(value: str | float | int | None) -> int | None:
    """Safely parse a string to int, returning None for missing/invalid values."""
    f = parse_float(value)
    if f is None:
        return None
    return int(f)


def parse_date(value: str | None) -> date | None:
    """Parse a YYYY-MM-DD string to a date, returning None on failure."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_datetime(value: str | None) -> datetime | None:
    """Parse a 'YYYY-MM-DD HH:MM:SS' string to datetime, returning None on failure."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def parse_percent(value: str | None) -> float | None:
    """Parse a percentage string to a decimal float.

    Examples:
        >>> parse_percent("1.23%")
        0.0123
        >>> parse_percent("None")
    """
    if value is None:
        return None
    value = value.strip().rstrip("%")
    f = parse_float(value)
    if f is None:
        return None
    return f / 100.0
