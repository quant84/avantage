"""Exception hierarchy for the avantage package."""

from __future__ import annotations

from typing import Any


class AlphaVantageError(Exception):
    """Base exception for all Alpha Vantage API errors."""

    def __init__(
        self,
        message: str,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.response_data = response_data
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class AuthenticationError(AlphaVantageError):
    """Raised when the API key is invalid or missing."""


class RateLimitError(AlphaVantageError):
    """Raised when the API rate limit has been exceeded."""

    def __init__(
        self,
        message: str,
        response_data: dict[str, Any] | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, response_data)
        self.retry_after = retry_after


class SymbolNotFoundError(AlphaVantageError):
    """Raised when a symbol is invalid or not recognized."""


class InvalidParameterError(AlphaVantageError):
    """Raised when request parameters are invalid."""


class APIResponseError(AlphaVantageError):
    """Raised when the upstream response is malformed or cannot be parsed."""


class UpstreamError(AlphaVantageError):
    """Raised on generic upstream failures (5xx, connectivity, etc.)."""
