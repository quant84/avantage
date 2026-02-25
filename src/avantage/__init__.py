"""Modern, fully-typed Python wrapper for the Alpha Vantage API."""

from __future__ import annotations

from avantage.client import AlphaVantageClient
from avantage.config import ClientConfig
from avantage.exceptions import (
    AlphaVantageError,
    APIResponseError,
    AuthenticationError,
    InvalidParameterError,
    RateLimitError,
    SymbolNotFoundError,
    UpstreamError,
)

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("avantage")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "AlphaVantageClient",
    "AlphaVantageError",
    "APIResponseError",
    "AuthenticationError",
    "ClientConfig",
    "InvalidParameterError",
    "RateLimitError",
    "SymbolNotFoundError",
    "UpstreamError",
    "__version__",
]
