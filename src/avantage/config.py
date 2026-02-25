"""Client configuration for the avantage package."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class ClientConfig(BaseModel):
    """Immutable configuration for :class:`AlphaVantageClient`.

    Args:
        api_key: Alpha Vantage API key.
        base_url: Base URL for the Alpha Vantage query endpoint.
        timeout: HTTP request timeout in seconds.
        max_retries: Maximum number of retry attempts on transient failures.
        retry_base_delay: Base delay in seconds for exponential backoff.
        retry_max_delay: Maximum delay in seconds between retries.
        rate_limit: Maximum requests per minute.
    """

    model_config = ConfigDict(frozen=True)

    api_key: str
    base_url: str = "https://www.alphavantage.co/query"
    timeout: float = 30.0
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    rate_limit: int = 75

    @field_validator("api_key")
    @classmethod
    def _api_key_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("api_key must not be empty")
        return v

    @field_validator("timeout")
    @classmethod
    def _timeout_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("timeout must be greater than 0")
        return v

    @field_validator("max_retries")
    @classmethod
    def _max_retries_at_least_one(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_retries must be at least 1")
        return v

    @field_validator("retry_base_delay")
    @classmethod
    def _retry_base_delay_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("retry_base_delay must be greater than 0")
        return v

    @field_validator("retry_max_delay")
    @classmethod
    def _retry_max_delay_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("retry_max_delay must be greater than 0")
        return v

    @field_validator("rate_limit")
    @classmethod
    def _rate_limit_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("rate_limit must be greater than 0")
        return v
