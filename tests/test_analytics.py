"""Tests for the AnalyticsAPI."""

from __future__ import annotations

from avantage.api.analytics import AnalyticsAPI

MOCK_FIXED = {
    "meta": {"symbols": "AAPL,MSFT", "range": "2024-01-01,2024-12-31"},
    "payload": {
        "AAPL": {"MEAN": 185.50, "STDDEV": 12.30},
        "MSFT": {"MEAN": 380.00, "STDDEV": 20.10},
    },
}

MOCK_SLIDING = {
    "meta": {"symbols": "AAPL", "range": "2024-01-01,2024-12-31", "window_size": 20},
    "payload": {
        "AAPL": [
            {"date": "2024-01-25", "MEAN": 186.00, "STDDEV": 3.50},
        ]
    },
}


async def test_fixed_window(mock_request):
    mock_request.return_value = MOCK_FIXED
    api = AnalyticsAPI(mock_request)
    result = await api.fixed_window("AAPL,MSFT", "2024-01-01,2024-12-31", "DAILY", "MEAN,STDDEV")

    assert isinstance(result, dict)
    assert result["payload"]["AAPL"]["MEAN"] == 185.50
    assert result["payload"]["MSFT"]["STDDEV"] == 20.10
    mock_request.assert_called_once_with(
        "ANALYTICS_FIXED_WINDOW",
        SYMBOLS="AAPL,MSFT",
        RANGE="2024-01-01,2024-12-31",
        INTERVAL="DAILY",
        CALCULATIONS="MEAN,STDDEV",
        OHLC="close",
    )


async def test_sliding_window(mock_request):
    mock_request.return_value = MOCK_SLIDING
    api = AnalyticsAPI(mock_request)
    result = await api.sliding_window("AAPL", "2024-01-01,2024-12-31", "DAILY", 20, "MEAN,STDDEV")

    assert isinstance(result, dict)
    assert result["payload"]["AAPL"][0]["MEAN"] == 186.00
    mock_request.assert_called_once_with(
        "ANALYTICS_SLIDING_WINDOW",
        SYMBOLS="AAPL",
        RANGE="2024-01-01,2024-12-31",
        INTERVAL="DAILY",
        WINDOW_SIZE=20,
        CALCULATIONS="MEAN,STDDEV",
        OHLC="close",
    )
