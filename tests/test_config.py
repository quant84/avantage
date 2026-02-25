"""Tests for ClientConfig validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from avantage import ClientConfig


class TestClientConfigValid:
    """Tests for valid config construction."""

    async def test_valid_config(self):
        cfg = ClientConfig(api_key="my_key")
        assert cfg.api_key == "my_key"

    async def test_defaults_are_correct(self):
        cfg = ClientConfig(api_key="k")
        assert cfg.base_url == "https://www.alphavantage.co/query"
        assert cfg.timeout == 30.0
        assert cfg.max_retries == 3
        assert cfg.retry_base_delay == 1.0
        assert cfg.retry_max_delay == 30.0
        assert cfg.rate_limit == 75

    async def test_custom_values(self):
        cfg = ClientConfig(
            api_key="k",
            timeout=10.0,
            max_retries=5,
            retry_base_delay=0.5,
            retry_max_delay=10.0,
            rate_limit=100,
        )
        assert cfg.timeout == 10.0
        assert cfg.max_retries == 5
        assert cfg.retry_base_delay == 0.5
        assert cfg.retry_max_delay == 10.0
        assert cfg.rate_limit == 100


class TestClientConfigRejections:
    """Tests for config validation errors."""

    async def test_empty_api_key_rejected(self):
        with pytest.raises(ValidationError, match="api_key must not be empty"):
            ClientConfig(api_key="")

    async def test_whitespace_api_key_rejected(self):
        with pytest.raises(ValidationError, match="api_key must not be empty"):
            ClientConfig(api_key="   ")

    async def test_timeout_zero_rejected(self):
        with pytest.raises(ValidationError, match="timeout must be greater than 0"):
            ClientConfig(api_key="k", timeout=0)

    async def test_timeout_negative_rejected(self):
        with pytest.raises(ValidationError, match="timeout must be greater than 0"):
            ClientConfig(api_key="k", timeout=-1)

    async def test_max_retries_zero_rejected(self):
        with pytest.raises(ValidationError, match="max_retries must be at least 1"):
            ClientConfig(api_key="k", max_retries=0)

    async def test_retry_base_delay_zero_rejected(self):
        with pytest.raises(ValidationError, match="retry_base_delay must be greater than 0"):
            ClientConfig(api_key="k", retry_base_delay=0)

    async def test_retry_max_delay_zero_rejected(self):
        with pytest.raises(ValidationError, match="retry_max_delay must be greater than 0"):
            ClientConfig(api_key="k", retry_max_delay=0)

    async def test_rate_limit_zero_rejected(self):
        with pytest.raises(ValidationError, match="rate_limit must be greater than 0"):
            ClientConfig(api_key="k", rate_limit=0)


class TestClientConfigFrozen:
    """Tests for config immutability."""

    async def test_config_is_frozen(self):
        cfg = ClientConfig(api_key="k")
        with pytest.raises(ValidationError):
            cfg.api_key = "new_key"

    async def test_config_frozen_timeout(self):
        cfg = ClientConfig(api_key="k")
        with pytest.raises(ValidationError):
            cfg.timeout = 99.0
