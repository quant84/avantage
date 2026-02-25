"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from avantage import AlphaVantageClient

BASE_URL = "https://www.alphavantage.co/query"


@pytest.fixture
def mock_request():
    """Create a mock request function that returns a configurable response."""
    return AsyncMock()


@pytest.fixture
async def client():
    """Create a real AlphaVantageClient with test config for respx mocking."""
    async with AlphaVantageClient(
        "test_key",
        max_retries=1,
        retry_base_delay=0.01,
        retry_max_delay=0.01,
        rate_limit=600,
    ) as c:
        yield c


@pytest.fixture
async def retry_client():
    """Client with 3 retries for retry tests."""
    async with AlphaVantageClient(
        "test_key",
        max_retries=3,
        retry_base_delay=0.01,
        retry_max_delay=0.01,
        rate_limit=600,
    ) as c:
        yield c
