"""Tests for AlphaVantageClient core request machinery."""

from __future__ import annotations

import asyncio
import time

import httpx
import pytest
import respx

from avantage.exceptions import (
    APIResponseError,
    AuthenticationError,
    InvalidParameterError,
    RateLimitError,
    SymbolNotFoundError,
    UpstreamError,
)
from avantage.rate_limiter import TokenBucketRateLimiter

BASE_URL = "https://www.alphavantage.co/query"


# ---------------------------------------------------------------------------
# Request mechanics
# ---------------------------------------------------------------------------
class TestRequestMechanics:
    """Verify query-param construction."""

    @respx.mock
    async def test_api_key_injected(self, client):
        route = respx.get(BASE_URL).respond(json={"result": "ok"})
        await client._request("TIME_SERIES_DAILY")
        assert route.called
        sent_params = dict(route.calls.last.request.url.params)
        assert sent_params["apikey"] == "test_key"

    @respx.mock
    async def test_function_name_injected(self, client):
        route = respx.get(BASE_URL).respond(json={"result": "ok"})
        await client._request("TIME_SERIES_DAILY")
        sent_params = dict(route.calls.last.request.url.params)
        assert sent_params["function"] == "TIME_SERIES_DAILY"

    @respx.mock
    async def test_extra_params_forwarded(self, client):
        route = respx.get(BASE_URL).respond(json={"result": "ok"})
        await client._request("TIME_SERIES_DAILY", symbol="AAPL", outputsize="full")
        sent_params = dict(route.calls.last.request.url.params)
        assert sent_params["symbol"] == "AAPL"
        assert sent_params["outputsize"] == "full"

    @respx.mock
    async def test_none_params_stripped(self, client):
        route = respx.get(BASE_URL).respond(json={"result": "ok"})
        await client._request("TIME_SERIES_DAILY", symbol="AAPL", outputsize=None)
        sent_params = dict(route.calls.last.request.url.params)
        assert "outputsize" not in sent_params
        assert sent_params["symbol"] == "AAPL"


# ---------------------------------------------------------------------------
# Error detection (business-logic errors in 200 responses)
# ---------------------------------------------------------------------------
class TestErrorDetection:
    """Verify that embedded error signals raise the right exceptions."""

    @respx.mock
    async def test_error_message_raises(self, client):
        respx.get(BASE_URL).respond(
            json={"Error Message": "something went wrong"},
        )
        with pytest.raises(InvalidParameterError):
            await client._request("TEST")

    @respx.mock
    async def test_note_call_frequency_raises_rate_limit(self, client):
        respx.get(BASE_URL).respond(
            json={
                "Note": "Thank you for using Alpha Vantage! "
                "Our standard API call frequency is 25 calls per day."
            },
        )
        with pytest.raises(RateLimitError):
            await client._request("TEST")

    @respx.mock
    async def test_invalid_api_key_raises_auth_error(self, client):
        respx.get(BASE_URL).respond(
            json={"Error Message": "the parameter apikey is invalid or missing"},
        )
        with pytest.raises(AuthenticationError):
            await client._request("TEST")

    @respx.mock
    async def test_symbol_not_found_raises(self, client):
        respx.get(BASE_URL).respond(
            json={"Error Message": "No data found for symbol XYZXYZ."},
        )
        with pytest.raises(SymbolNotFoundError):
            await client._request("TEST")

    @respx.mock
    async def test_non_json_response_raises_api_response_error(self, client):
        respx.get(BASE_URL).respond(
            content=b"<html>Server Error</html>",
            headers={"Content-Type": "text/html"},
        )
        with pytest.raises(APIResponseError, match="Failed to parse JSON"):
            await client._request("TEST")


# ---------------------------------------------------------------------------
# HTTP error handling
# ---------------------------------------------------------------------------
class TestHTTPErrors:
    """Verify HTTP status code handling."""

    @respx.mock
    async def test_http_500_raises_upstream_error(self, client):
        respx.get(BASE_URL).respond(status_code=500)
        with pytest.raises(UpstreamError, match="HTTP 500"):
            await client._request("TEST")

    @respx.mock
    async def test_http_400_raises_upstream_no_retry(self, client):
        route = respx.get(BASE_URL).respond(status_code=400)
        with pytest.raises(UpstreamError, match="HTTP 400"):
            await client._request("TEST")
        # Client has max_retries=1, but 400 is not retryable so only 1 call.
        assert route.call_count == 1


# ---------------------------------------------------------------------------
# Retry behavior (use retry_client with max_retries=3)
# ---------------------------------------------------------------------------
class TestRetryBehavior:
    """Verify retry logic for transient failures."""

    @respx.mock
    async def test_retries_on_500_then_succeeds(self, retry_client):
        route = respx.get(BASE_URL).mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(200, json={"result": "ok"}),
            ]
        )
        result = await retry_client._request("TEST")
        assert result == {"result": "ok"}
        assert route.call_count == 2

    @respx.mock
    async def test_retries_on_502_then_succeeds(self, retry_client):
        route = respx.get(BASE_URL).mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(200, json={"result": "ok"}),
            ]
        )
        result = await retry_client._request("TEST")
        assert result == {"result": "ok"}
        assert route.call_count == 2

    @respx.mock
    async def test_exhausts_retries_raises_upstream(self, retry_client):
        route = respx.get(BASE_URL).mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(500),
                httpx.Response(500),
            ]
        )
        with pytest.raises(UpstreamError, match="HTTP 500"):
            await retry_client._request("TEST")
        assert route.call_count == 3

    @respx.mock
    async def test_retries_on_connect_error_then_succeeds(self, retry_client):
        route = respx.get(BASE_URL).mock(
            side_effect=[
                httpx.ConnectError("connection refused"),
                httpx.Response(200, json={"result": "ok"}),
            ]
        )
        result = await retry_client._request("TEST")
        assert result == {"result": "ok"}
        assert route.call_count == 2

    @respx.mock
    async def test_no_retry_on_400(self, retry_client):
        route = respx.get(BASE_URL).respond(status_code=400)
        with pytest.raises(UpstreamError, match="HTTP 400"):
            await retry_client._request("TEST")
        # 400 is not retryable: should be exactly 1 call.
        assert route.call_count == 1


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
class TestRateLimiter:
    """Verify TokenBucketRateLimiter behavior."""

    async def test_acquire_succeeds_immediately(self):
        limiter = TokenBucketRateLimiter(rate=10, period=60.0)
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.05

    async def test_acquire_waits_when_empty(self):
        limiter = TokenBucketRateLimiter(rate=1, period=0.5)
        # Drain the single token.
        await limiter.acquire()
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        # Should have waited roughly 0.5s (the period for 1 token).
        assert elapsed >= 0.3

    async def test_no_overshoot_under_concurrency(self):
        rate = 5
        limiter = TokenBucketRateLimiter(rate=rate, period=60.0)

        acquired = 0
        fast_acquired = 0

        async def grab():
            nonlocal acquired, fast_acquired
            start = time.monotonic()
            await limiter.acquire()
            elapsed = time.monotonic() - start
            acquired += 1
            if elapsed < 0.05:
                fast_acquired += 1

        # Launch 10 concurrent grabs; only `rate` should complete immediately.
        tasks = [asyncio.create_task(grab()) for _ in range(10)]
        # Let the fast ones complete; give a small window.
        await asyncio.sleep(0.1)

        # At most `rate` should have acquired without waiting.
        assert fast_acquired <= rate

        # Clean up remaining tasks -- cancel and suppress CancelledError.
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
