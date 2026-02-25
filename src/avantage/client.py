"""Core Alpha Vantage API client with async HTTP, retries, and rate limiting."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import httpx

from avantage.config import ClientConfig
from avantage.exceptions import (
    APIResponseError,
    AuthenticationError,
    InvalidParameterError,
    RateLimitError,
    SymbolNotFoundError,
    UpstreamError,
)
from avantage.rate_limiter import TokenBucketRateLimiter

logger = logging.getLogger("avantage")

# HTTP status codes that trigger a retry.
_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class AlphaVantageClient:
    """Async-first client for the Alpha Vantage financial data API.

    Args:
        api_key: Your Alpha Vantage API key.
        **kwargs: Additional keyword arguments forwarded to :class:`ClientConfig`.

    Example::

        async with AlphaVantageClient("YOUR_KEY") as client:
            data = await client.equity.daily("AAPL")
    """

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        self._config = ClientConfig(api_key=api_key, **kwargs)
        self._rate_limiter = TokenBucketRateLimiter(rate=self._config.rate_limit)
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(self._config.timeout),
            headers={"User-Agent": "avantage-python"},
        )

        # API group singletons -- wired in Phase 2.
        self._equity: Any = None
        self._forex: Any = None
        self._crypto: Any = None
        self._commodities: Any = None
        self._fundamentals: Any = None
        self._economic: Any = None
        self._indicators: Any = None
        self._intelligence: Any = None
        self._options: Any = None
        self._analytics: Any = None
        self._calendar: Any = None

    # -- Context manager --------------------------------------------------

    async def __aenter__(self) -> AlphaVantageClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        await self._http.aclose()

    # -- Internal request machinery ---------------------------------------

    async def _request(self, function: str, **params: Any) -> dict[str, Any]:
        """Send a request to the Alpha Vantage API with retries and rate limiting.

        Args:
            function: The Alpha Vantage function name (e.g. ``TIME_SERIES_DAILY``).
            **params: Additional query parameters forwarded to the API.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the API rate limit is exceeded.
            SymbolNotFoundError: If the requested symbol does not exist.
            InvalidParameterError: If request parameters are rejected.
            APIResponseError: If the response cannot be parsed.
            UpstreamError: On transient upstream failures after all retries.
        """
        query: dict[str, Any] = {
            "function": function,
            "apikey": self._config.api_key,
            "datatype": "json",
            **{k: v for k, v in params.items() if v is not None},
        }

        last_exc: Exception | None = None

        for attempt in range(1, self._config.max_retries + 1):
            await self._rate_limiter.acquire()

            try:
                resp = await self._http.get(self._config.base_url, params=query)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "Request attempt %d/%d failed: %s",
                    attempt,
                    self._config.max_retries,
                    exc,
                )
                if attempt < self._config.max_retries:
                    await self._backoff(attempt)
                    continue
                raise UpstreamError(
                    f"Connection failed after {self._config.max_retries} attempts: {exc}",
                ) from exc

            # Retryable HTTP status codes.
            if resp.status_code in _RETRYABLE_STATUS_CODES:
                last_exc = UpstreamError(
                    f"HTTP {resp.status_code}",
                    response_data={"status_code": resp.status_code},
                )
                logger.warning(
                    "Request attempt %d/%d received HTTP %d",
                    attempt,
                    self._config.max_retries,
                    resp.status_code,
                )
                if attempt < self._config.max_retries:
                    await self._backoff(attempt)
                    continue
                raise last_exc

            # Non-retryable HTTP errors.
            if resp.status_code != 200:
                raise UpstreamError(
                    f"HTTP {resp.status_code}",
                    response_data={"status_code": resp.status_code},
                )

            # Parse JSON body.
            try:
                data: dict[str, Any] = resp.json()
            except Exception as exc:
                raise APIResponseError(
                    f"Failed to parse JSON response: {exc}",
                ) from exc

            # Detect business-logic errors embedded in the response.
            self._check_response_errors(data)
            return data

        # Should not reach here, but satisfy the type checker.
        raise UpstreamError(  # pragma: no cover
            f"Request failed after {self._config.max_retries} attempts",
        )

    def _check_response_errors(self, data: dict[str, Any]) -> None:
        """Inspect a parsed response for embedded error signals."""
        error_msg = data.get("Error Message")
        if error_msg:
            lower = str(error_msg).lower()
            if "invalid api" in lower or "apikey" in lower:
                raise AuthenticationError(str(error_msg), response_data=data)
            if "symbol" in lower or "not found" in lower:
                raise SymbolNotFoundError(str(error_msg), response_data=data)
            raise InvalidParameterError(str(error_msg), response_data=data)

        note = data.get("Note") or data.get("Information")
        if note:
            lower = str(note).lower()
            if "rate limit" in lower or "call frequency" in lower:
                raise RateLimitError(str(note), response_data=data)
            if "invalid api" in lower or "premium" in lower:
                raise AuthenticationError(str(note), response_data=data)
            # Some "Information" messages are benign; treat unknown ones as errors.
            raise APIResponseError(str(note), response_data=data)

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff and full jitter."""
        exp_delay = self._config.retry_base_delay * (2 ** (attempt - 1))
        capped = min(exp_delay, self._config.retry_max_delay)
        jittered = random.uniform(0, capped)  # noqa: S311
        logger.debug("Backing off %.2fs before retry %d", jittered, attempt + 1)
        await asyncio.sleep(jittered)

    # -- Lazy API group properties (wired in Phase 2) ---------------------

    @property
    def equity(self) -> Any:
        """Equity (stock) time series endpoints."""
        if self._equity is None:
            from avantage.api.equity import EquityAPI  # wired in Phase 2

            self._equity = EquityAPI(self._request)
        return self._equity

    @property
    def forex(self) -> Any:
        """Foreign exchange rate endpoints."""
        if self._forex is None:
            from avantage.api.forex import ForexAPI  # wired in Phase 2

            self._forex = ForexAPI(self._request)
        return self._forex

    @property
    def crypto(self) -> Any:
        """Cryptocurrency endpoints."""
        if self._crypto is None:
            from avantage.api.crypto import CryptoAPI  # wired in Phase 2

            self._crypto = CryptoAPI(self._request)
        return self._crypto

    @property
    def commodities(self) -> Any:
        """Commodity price endpoints."""
        if self._commodities is None:
            from avantage.api.commodities import CommoditiesAPI  # wired in Phase 2

            self._commodities = CommoditiesAPI(self._request)
        return self._commodities

    @property
    def fundamentals(self) -> Any:
        """Fundamental data endpoints (income statement, balance sheet, etc.)."""
        if self._fundamentals is None:
            from avantage.api.fundamentals import FundamentalsAPI  # wired in Phase 2

            self._fundamentals = FundamentalsAPI(self._request)
        return self._fundamentals

    @property
    def economic(self) -> Any:
        """Economic indicator endpoints (GDP, CPI, etc.)."""
        if self._economic is None:
            from avantage.api.economic import EconomicAPI  # wired in Phase 2

            self._economic = EconomicAPI(self._request)
        return self._economic

    @property
    def indicators(self) -> Any:
        """Technical indicator endpoints (SMA, RSI, MACD, etc.)."""
        if self._indicators is None:
            from avantage.api.indicators import IndicatorsAPI  # wired in Phase 2

            self._indicators = IndicatorsAPI(self._request)
        return self._indicators

    @property
    def intelligence(self) -> Any:
        """Alpha Intelligence endpoints (news, sentiment, etc.)."""
        if self._intelligence is None:
            from avantage.api.intelligence import IntelligenceAPI  # wired in Phase 2

            self._intelligence = IntelligenceAPI(self._request)
        return self._intelligence

    @property
    def options(self) -> Any:
        """Options data endpoints."""
        if self._options is None:
            from avantage.api.options import OptionsAPI  # wired in Phase 2

            self._options = OptionsAPI(self._request)
        return self._options

    @property
    def analytics(self) -> Any:
        """Fixed-window analytics endpoints."""
        if self._analytics is None:
            from avantage.api.analytics import AnalyticsAPI  # wired in Phase 2

            self._analytics = AnalyticsAPI(self._request)
        return self._analytics

    @property
    def calendar(self) -> Any:
        """IPO and earnings calendar endpoints."""
        if self._calendar is None:
            from avantage.api.calendar import CalendarAPI  # wired in Phase 2

            self._calendar = CalendarAPI(self._request)
        return self._calendar
