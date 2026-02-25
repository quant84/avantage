"""Modern, fully-typed Python wrapper for the Alpha Vantage API."""

from __future__ import annotations

try:
    from importlib.metadata import version

    __version__ = version("avantage")
except Exception:
    __version__ = "0.0.0"
