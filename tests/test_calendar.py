"""Tests for the CalendarAPI."""

from __future__ import annotations

from avantage.api.calendar import CalendarAPI

MOCK_EARNINGS = {
    "data": [
        {
            "symbol": "AAPL",
            "reportDate": "2024-01-25",
            "fiscalDateEnding": "2024-12-31",
        }
    ]
}

MOCK_IPO = {
    "data": [
        {
            "symbol": "NEWCO",
            "name": "New Company Inc",
            "ipoDate": "2024-03-15",
            "exchange": "NASDAQ",
        }
    ]
}


async def test_earnings(mock_request):
    mock_request.return_value = MOCK_EARNINGS
    api = CalendarAPI(mock_request)
    result = await api.earnings(symbol="AAPL")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["reportDate"] == "2024-01-25"
    assert result[0]["fiscalDateEnding"] == "2024-12-31"
    mock_request.assert_called_once_with("EARNINGS_CALENDAR", symbol="AAPL", horizon="3month")


async def test_ipo(mock_request):
    mock_request.return_value = MOCK_IPO
    api = CalendarAPI(mock_request)
    result = await api.ipo()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["symbol"] == "NEWCO"
    assert result[0]["name"] == "New Company Inc"
    assert result[0]["ipoDate"] == "2024-03-15"
    mock_request.assert_called_once_with("IPO_CALENDAR")
