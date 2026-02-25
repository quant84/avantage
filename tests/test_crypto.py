"""Tests for CryptoAPI."""

from __future__ import annotations

from avantage.api.crypto import CryptoAPI
from avantage.models.crypto import CryptoDataPoint
from avantage.models.forex import ExchangeRate

# ---------------------------------------------------------------------------
# Shared mock data
# ---------------------------------------------------------------------------

_EXCHANGE_RATE_RESPONSE = {
    "Realtime Currency Exchange Rate": {
        "1. From_Currency Code": "BTC",
        "2. From_Currency Name": "Bitcoin",
        "3. To_Currency Code": "USD",
        "4. To_Currency Name": "United States Dollar",
        "5. Exchange Rate": "42500.00",
        "6. Last Refreshed": "2024-01-02 12:00:00",
        "7. Time Zone": "UTC",
        "8. Bid Price": "42499.00",
        "9. Ask Price": "42501.00",
    }
}

_CRYPTO_INTRADAY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Crypto Intraday (1min)",
        "2. Digital Currency Code": "BTC",
        "3. Digital Currency Name": "Bitcoin",
        "4. Market Code": "USD",
        "5. Market Name": "United States Dollar",
    },
    "Time Series Crypto (1min)": {
        "2024-01-02 12:00:00": {
            "1. open": "42000.00",
            "2. high": "42100.00",
            "3. low": "41900.00",
            "4. close": "42050.00",
            "5. volume": "100.5",
        }
    },
}

_CRYPTO_DAILY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Daily Prices (Digital Currency)",
        "2. Digital Currency Code": "BTC",
        "3. Digital Currency Name": "Bitcoin",
        "4. Market Code": "USD",
        "5. Market Name": "United States Dollar",
    },
    "Time Series (Digital Currency Daily)": {
        "2024-01-02": {
            "1a. open (USD)": "42000.00",
            "1b. open (USD)": "42000.00",
            "2a. high (USD)": "43000.00",
            "2b. high (USD)": "43000.00",
            "3a. low (USD)": "41000.00",
            "3b. low (USD)": "41000.00",
            "4a. close (USD)": "42500.00",
            "4b. close (USD)": "42500.00",
            "5. volume": "1234.5678",
            "6. market cap (USD)": "850000000000.00",
        }
    },
}

_CRYPTO_WEEKLY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Weekly Prices (Digital Currency)",
        "2. Digital Currency Code": "BTC",
    },
    "Time Series (Digital Currency Weekly)": {
        "2024-01-05": {
            "1a. open (USD)": "42000.00",
            "1b. open (USD)": "42000.00",
            "2a. high (USD)": "44000.00",
            "2b. high (USD)": "44000.00",
            "3a. low (USD)": "41000.00",
            "3b. low (USD)": "41000.00",
            "4a. close (USD)": "43500.00",
            "4b. close (USD)": "43500.00",
            "5. volume": "5678.1234",
            "6. market cap (USD)": "870000000000.00",
        }
    },
}

_CRYPTO_MONTHLY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Monthly Prices (Digital Currency)",
        "2. Digital Currency Code": "BTC",
    },
    "Time Series (Digital Currency Monthly)": {
        "2024-01-31": {
            "1a. open (USD)": "42000.00",
            "1b. open (USD)": "42000.00",
            "2a. high (USD)": "48000.00",
            "2b. high (USD)": "48000.00",
            "3a. low (USD)": "40000.00",
            "3b. low (USD)": "40000.00",
            "4a. close (USD)": "46000.00",
            "4b. close (USD)": "46000.00",
            "5. volume": "9999.0000",
            "6. market cap (USD)": "920000000000.00",
        }
    },
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_exchange_rate(mock_request):
    mock_request.return_value = _EXCHANGE_RATE_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.exchange_rate("BTC", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, ExchangeRate)
    assert result.from_currency_code == "BTC"
    assert result.to_currency_code == "USD"
    assert result.exchange_rate == 42500.0


async def test_intraday(mock_request):
    mock_request.return_value = _CRYPTO_INTRADAY_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.intraday("BTC", "USD", "1min")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    point = result[0]
    assert isinstance(point, CryptoDataPoint)
    assert point.timestamp == "2024-01-02 12:00:00"
    assert point.open == 42000.0
    assert point.high == 42100.0
    assert point.low == 41900.0
    assert point.close == 42050.0
    assert point.volume == 100.5


async def test_daily(mock_request):
    mock_request.return_value = _CRYPTO_DAILY_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.daily("BTC", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    point = result[0]
    assert isinstance(point, CryptoDataPoint)
    assert point.timestamp == "2024-01-02"
    assert point.open == 42000.0
    assert point.high == 43000.0
    assert point.low == 41000.0
    assert point.close == 42500.0


async def test_daily_volume_and_market_cap(mock_request):
    mock_request.return_value = _CRYPTO_DAILY_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.daily("BTC", "USD")
    point = result[0]

    assert point.volume == 1234.5678
    assert isinstance(point.volume, float)
    assert point.market_cap == 850000000000.0
    assert isinstance(point.market_cap, float)


async def test_weekly(mock_request):
    mock_request.return_value = _CRYPTO_WEEKLY_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.weekly("BTC", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    point = result[0]
    assert isinstance(point, CryptoDataPoint)
    assert point.close == 43500.0
    assert point.volume == 5678.1234


async def test_monthly(mock_request):
    mock_request.return_value = _CRYPTO_MONTHLY_RESPONSE
    api = CryptoAPI(mock_request)

    result = await api.monthly("BTC", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    point = result[0]
    assert isinstance(point, CryptoDataPoint)
    assert point.close == 46000.0
    assert point.market_cap == 920000000000.0
