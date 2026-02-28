"""Tests for EquityAPI."""

from __future__ import annotations

from avantage.api.equity import EquityAPI
from avantage.models.common import TimeSeriesResponse
from avantage.models.equity import BulkQuoteEntry, GlobalQuote, MarketStatus, SymbolMatch

# ---------------------------------------------------------------------------
# Shared mock data
# ---------------------------------------------------------------------------

_META = {"1. Information": "Daily Prices", "2. Symbol": "AAPL"}

_OHLCV = {
    "1. open": "150.00",
    "2. high": "155.00",
    "3. low": "149.00",
    "4. close": "154.00",
    "5. volume": "1000000",
}

_OHLCV_ADJUSTED = {
    **_OHLCV,
    "5. adjusted close": "153.50",
    "6. volume": "1000000",
    "7. dividend amount": "0.24",
    "8. split coefficient": "1.0",
}

_DAILY_RESPONSE = {
    "Meta Data": _META,
    "Time Series (Daily)": {"2024-01-02": _OHLCV},
}

_DAILY_ADJ_RESPONSE = {
    "Meta Data": _META,
    "Time Series (Daily)": {
        "2024-01-02": _OHLCV_ADJUSTED,
    },
}

_INTRADAY_RESPONSE = {
    "Meta Data": {
        "1. Information": "Intraday (5min)",
        "2. Symbol": "AAPL",
    },
    "Time Series (5min)": {"2024-01-02 10:00:00": _OHLCV},
}

_WEEKLY_RESPONSE = {
    "Meta Data": _META,
    "Weekly Time Series": {"2024-01-05": _OHLCV},
}

_WEEKLY_ADJ_RESPONSE = {
    "Meta Data": _META,
    "Weekly Adjusted Time Series": {
        "2024-01-05": _OHLCV_ADJUSTED,
    },
}

_MONTHLY_RESPONSE = {
    "Meta Data": _META,
    "Monthly Time Series": {"2024-01-31": _OHLCV},
}

_MONTHLY_ADJ_RESPONSE = {
    "Meta Data": _META,
    "Monthly Adjusted Time Series": {
        "2024-01-31": _OHLCV_ADJUSTED,
    },
}

_QUOTE_RESPONSE = {
    "Global Quote": {
        "01. symbol": "AAPL",
        "02. open": "150.00",
        "03. high": "155.00",
        "04. low": "149.00",
        "05. price": "154.00",
        "06. volume": "1000000",
        "07. latest trading day": "2024-01-02",
        "08. previous close": "152.00",
        "09. change": "2.00",
        "10. change percent": "1.32%",
    }
}

_BULK_RESPONSE = {
    "data": [
        {
            "symbol": "AAPL",
            "open": "150.00",
            "high": "155.00",
            "low": "149.00",
            "price": "154.00",
            "volume": "1000000",
            "latest_trading_day": "2024-01-02",
            "previous_close": "152.00",
            "change": "2.00",
            "change_percent": "1.32%",
        },
        {
            "symbol": "MSFT",
            "open": "370.00",
            "high": "375.00",
            "low": "368.00",
            "price": "374.00",
            "volume": "500000",
            "latest_trading_day": "2024-01-02",
            "previous_close": "371.00",
            "change": "3.00",
            "change_percent": "0.81%",
        },
    ]
}

_BULK_RESPONSE_REALTIME = {
    "data": [
        {
            "symbol": "AAPL",
            "open": "150.00",
            "high": "155.00",
            "low": "149.00",
            "close": "154.00",
            "volume": "1000000",
            "previous_close": "152.00",
            "change": "2.00",
            "change_percent": "1.32%",
        },
        {
            "symbol": "MSFT",
            "open": "370.00",
            "high": "375.00",
            "low": "368.00",
            "close": "374.00",
            "volume": "500000",
            "previous_close": "371.00",
            "change": "3.00",
            "change_percent": "0.81%",
        },
    ]
}

_SEARCH_RESPONSE = {
    "bestMatches": [
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc",
            "3. type": "Equity",
            "4. region": "United States",
            "5. marketOpen": "09:30",
            "6. marketClose": "16:00",
            "7. timezone": "UTC-05",
            "8. currency": "USD",
            "9. matchScore": "1.0000",
        }
    ]
}

_MARKET_STATUS_RESPONSE = {
    "markets": [
        {
            "market_type": "Equity",
            "region": "United States",
            "primary_exchanges": "NYSE, NASDAQ",
            "local_open": "09:30",
            "local_close": "16:00",
            "current_status": "open",
            "notes": "",
        }
    ]
}


# ---------------------------------------------------------------------------
# Time series tests
# ---------------------------------------------------------------------------


async def test_intraday(mock_request):
    mock_request.return_value = _INTRADAY_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.intraday("AAPL", "5min")

    mock_request.assert_called_once()
    assert isinstance(result, TimeSeriesResponse)
    assert len(result.data) == 1
    assert result.data[0].timestamp == "2024-01-02 10:00:00"
    assert result.data[0].open == 150.0
    assert result.data[0].close == 154.0
    assert result.data[0].volume == 1000000


async def test_daily(mock_request):
    mock_request.return_value = _DAILY_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.daily("AAPL")

    mock_request.assert_called_once()
    assert isinstance(result, TimeSeriesResponse)
    assert len(result.data) == 1
    entry = result.data[0]
    assert entry.timestamp == "2024-01-02"
    assert entry.open == 150.0
    assert entry.high == 155.0
    assert entry.low == 149.0
    assert entry.close == 154.0
    assert entry.volume == 1000000


async def test_daily_adjusted(mock_request):
    mock_request.return_value = _DAILY_ADJ_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.daily_adjusted("AAPL")

    mock_request.assert_called_once()
    assert len(result.data) == 1
    entry = result.data[0]
    assert entry.adjusted_close == 153.5
    assert entry.dividend_amount == 0.24
    assert entry.split_coefficient == 1.0


async def test_weekly(mock_request):
    mock_request.return_value = _WEEKLY_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.weekly("AAPL")

    mock_request.assert_called_once()
    assert isinstance(result, TimeSeriesResponse)
    assert len(result.data) == 1
    assert result.data[0].close == 154.0


async def test_weekly_adjusted(mock_request):
    mock_request.return_value = _WEEKLY_ADJ_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.weekly_adjusted("AAPL")

    mock_request.assert_called_once()
    assert len(result.data) == 1
    assert result.data[0].adjusted_close == 153.5


async def test_monthly(mock_request):
    mock_request.return_value = _MONTHLY_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.monthly("AAPL")

    mock_request.assert_called_once()
    assert isinstance(result, TimeSeriesResponse)
    assert len(result.data) == 1
    assert result.data[0].close == 154.0


async def test_monthly_adjusted(mock_request):
    mock_request.return_value = _MONTHLY_ADJ_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.monthly_adjusted("AAPL")

    mock_request.assert_called_once()
    assert len(result.data) == 1
    assert result.data[0].adjusted_close == 153.5


# ---------------------------------------------------------------------------
# Quote / search / market status tests
# ---------------------------------------------------------------------------


async def test_quote(mock_request):
    mock_request.return_value = _QUOTE_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.quote("AAPL")

    mock_request.assert_called_once()
    assert isinstance(result, GlobalQuote)
    assert result.symbol == "AAPL"
    assert result.open == 150.0
    assert result.high == 155.0
    assert result.low == 149.0
    assert result.price == 154.0
    assert result.volume == 1000000
    assert result.latest_trading_day == "2024-01-02"
    assert result.previous_close == 152.0
    assert result.change == 2.0
    assert result.change_percent == "1.32%"


async def test_bulk_quotes(mock_request):
    mock_request.return_value = _BULK_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.bulk_quotes("AAPL,MSFT")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(e, BulkQuoteEntry) for e in result)
    assert result[0].symbol == "AAPL"
    assert result[0].price == 154.0
    assert result[1].symbol == "MSFT"
    assert result[1].price == 374.0


async def test_bulk_quotes_realtime_close_field(mock_request):
    mock_request.return_value = _BULK_RESPONSE_REALTIME
    api = EquityAPI(mock_request)

    result = await api.bulk_quotes("AAPL,MSFT", entitlement="realtime")

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].symbol == "AAPL"
    assert result[0].price == 154.0
    assert result[1].symbol == "MSFT"
    assert result[1].price == 374.0


async def test_search(mock_request):
    mock_request.return_value = _SEARCH_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.search("Apple")

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    match = result[0]
    assert isinstance(match, SymbolMatch)
    assert match.symbol == "AAPL"
    assert match.name == "Apple Inc"
    assert match.type == "Equity"
    assert match.region == "United States"
    assert match.currency == "USD"
    assert match.match_score == "1.0000"


async def test_market_status(mock_request):
    mock_request.return_value = _MARKET_STATUS_RESPONSE
    api = EquityAPI(mock_request)

    result = await api.market_status()

    mock_request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    status = result[0]
    assert isinstance(status, MarketStatus)
    assert status.market_type == "Equity"
    assert status.region == "United States"
    assert status.primary_exchanges == "NYSE, NASDAQ"
    assert status.current_status == "open"
