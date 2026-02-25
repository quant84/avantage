"""Tests for ForexAPI."""

from __future__ import annotations

from avantage.api.forex import ForexAPI
from avantage.models.forex import ExchangeRate, FXDataPoint

# ---------------------------------------------------------------------------
# Shared mock data
# ---------------------------------------------------------------------------

_EXCHANGE_RATE_RESPONSE = {
    "Realtime Currency Exchange Rate": {
        "1. From_Currency Code": "USD",
        "2. From_Currency Name": "United States Dollar",
        "3. To_Currency Code": "EUR",
        "4. To_Currency Name": "Euro",
        "5. Exchange Rate": "0.8500",
        "6. Last Refreshed": "2024-01-02 12:00:00",
        "7. Time Zone": "UTC",
        "8. Bid Price": "0.8499",
        "9. Ask Price": "0.8501",
    }
}

_FX_OHLC = {
    "1. open": "0.8500",
    "2. high": "0.8600",
    "3. low": "0.8400",
    "4. close": "0.8550",
}

_FX_DAILY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Forex Daily Prices",
        "2. From Symbol": "USD",
        "3. To Symbol": "EUR",
    },
    "Time Series FX (Daily)": {"2024-01-02": _FX_OHLC},
}

_FX_INTRADAY_RESPONSE = {
    "Meta Data": {
        "1. Information": "FX Intraday (5min)",
        "2. From Symbol": "EUR",
        "3. To Symbol": "USD",
    },
    "Time Series FX (Intraday)": {"2024-01-02 12:00:00": _FX_OHLC},
}

_FX_WEEKLY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Forex Weekly Prices",
        "2. From Symbol": "EUR",
        "3. To Symbol": "USD",
    },
    "Time Series FX (Weekly)": {"2024-01-05": _FX_OHLC},
}

_FX_MONTHLY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Forex Monthly Prices",
        "2. From Symbol": "EUR",
        "3. To Symbol": "USD",
    },
    "Time Series FX (Monthly)": {"2024-01-31": _FX_OHLC},
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_exchange_rate(mock_request):
    mock_request.return_value = _EXCHANGE_RATE_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.exchange_rate("USD", "EUR")

    mock_request.assert_called_once()
    assert isinstance(result, ExchangeRate)
    assert result.from_currency_code == "USD"
    assert result.from_currency_name == "United States Dollar"
    assert result.to_currency_code == "EUR"
    assert result.to_currency_name == "Euro"
    assert result.exchange_rate == 0.85
    assert result.last_refreshed == "2024-01-02 12:00:00"
    assert result.timezone == "UTC"


async def test_exchange_rate_bid_ask(mock_request):
    mock_request.return_value = _EXCHANGE_RATE_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.exchange_rate("USD", "EUR")

    assert result.bid_price == 0.8499
    assert result.ask_price == 0.8501
    assert isinstance(result.bid_price, float)
    assert isinstance(result.ask_price, float)


async def test_intraday(mock_request):
    mock_request.return_value = _FX_INTRADAY_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.intraday("EUR", "USD", "5min")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FXDataPoint)
    assert result[0].timestamp == "2024-01-02 12:00:00"


async def test_daily(mock_request):
    mock_request.return_value = _FX_DAILY_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.daily("USD", "EUR")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    point = result[0]
    assert isinstance(point, FXDataPoint)
    assert point.timestamp == "2024-01-02"
    assert point.open == 0.85
    assert point.high == 0.86
    assert point.low == 0.84
    assert point.close == 0.855


async def test_weekly(mock_request):
    mock_request.return_value = _FX_WEEKLY_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.weekly("EUR", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FXDataPoint)
    assert result[0].close == 0.855


async def test_monthly(mock_request):
    mock_request.return_value = _FX_MONTHLY_RESPONSE
    api = ForexAPI(mock_request)

    result = await api.monthly("EUR", "USD")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FXDataPoint)
    assert result[0].close == 0.855
