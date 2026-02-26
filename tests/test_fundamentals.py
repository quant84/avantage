"""Tests for the FundamentalsAPI."""

from __future__ import annotations

from unittest.mock import AsyncMock

from avantage.api.fundamentals import FundamentalsAPI
from avantage.models.fundamentals import (
    CompanyOverview,
    DividendEntry,
    EarningsEntry,
    EarningsResponse,
    FinancialResponse,
    InsiderTransaction,
    ListingEntry,
    SplitEntry,
)

MOCK_OVERVIEW = {
    "Symbol": "AAPL",
    "Name": "Apple Inc",
    "Description": "Apple designs...",
    "Exchange": "NASDAQ",
    "Currency": "USD",
    "Country": "USA",
    "Sector": "TECHNOLOGY",
    "Industry": "ELECTRONIC COMPUTERS",
    "MarketCapitalization": "2800000000000",
    "PERatio": "28.5",
    "BookValue": "4.15",
    "DividendPerShare": "0.96",
    "DividendYield": "0.0055",
    "EPS": "6.42",
    "Beta": "1.27",
    "52WeekHigh": "199.62",
    "52WeekLow": "155.98",
    "50DayMovingAverage": "188.52",
    "200DayMovingAverage": "180.34",
    "SharesOutstanding": "15000000000",
}

MOCK_INCOME = {
    "symbol": "AAPL",
    "annualReports": [
        {
            "fiscalDateEnding": "2024-09-30",
            "reportedCurrency": "USD",
            "totalRevenue": "383285000000",
            "netIncome": "93736000000",
        }
    ],
    "quarterlyReports": [
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedCurrency": "USD",
            "totalRevenue": "95000000000",
        }
    ],
}

MOCK_EARNINGS = {
    "symbol": "AAPL",
    "annualEarnings": [{"fiscalDateEnding": "2024-09-30", "reportedEPS": "6.42"}],
    "quarterlyEarnings": [
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedEPS": "1.65",
            "estimatedEPS": "1.60",
            "surprise": "0.05",
            "surprisePercentage": "3.125",
        }
    ],
}

MOCK_DIVIDENDS = {
    "data": [
        {
            "ex_dividend_date": "2024-11-08",
            "declaration_date": "2024-11-01",
            "record_date": "2024-11-11",
            "payment_date": "2024-11-14",
            "amount": "0.25",
        }
    ]
}

MOCK_SPLITS = {"data": [{"effective_date": "2020-08-31", "split_ratio": "4:1"}]}

MOCK_INSIDER_TRANSACTIONS = {
    "data": [
        {
            "transaction_date": "2026-02-18",
            "ticker": "IBM",
            "executive": "KRISHNA, ARVIND",
            "executive_title": "Director, Chairman, President & CEO",
            "security_type": "Common Stock",
            "acquisition_or_disposal": "A",
            "shares": "5664.0",
            "share_price": "0.0",
        },
        {
            "transaction_date": "2026-02-18",
            "ticker": "IBM",
            "executive": "KRISHNA, ARVIND",
            "executive_title": "Director, Chairman, President & CEO",
            "security_type": "Common Stock",
            "acquisition_or_disposal": "D",
            "shares": "2839.0",
            "share_price": "258.68",
        },
    ]
}


async def test_overview(mock_request):
    mock_request.return_value = MOCK_OVERVIEW
    api = FundamentalsAPI(mock_request)
    result = await api.overview("AAPL")

    assert isinstance(result, CompanyOverview)
    assert result.symbol == "AAPL"
    assert result.name == "Apple Inc"
    assert result.exchange == "NASDAQ"
    assert result.sector == "TECHNOLOGY"
    assert result.market_capitalization == 2800000000000.0
    assert result.pe_ratio == 28.5
    assert result.eps == 6.42
    assert result.beta == 1.27
    assert result.week_52_high == 199.62
    assert result.week_52_low == 155.98
    assert result.moving_average_50 == 188.52
    assert result.moving_average_200 == 180.34
    assert result.shares_outstanding == 15000000000.0
    mock_request.assert_called_once_with("OVERVIEW", symbol="AAPL")


async def test_income_statement(mock_request):
    mock_request.return_value = MOCK_INCOME
    api = FundamentalsAPI(mock_request)
    result = await api.income_statement("AAPL")

    assert isinstance(result, FinancialResponse)
    assert result.symbol == "AAPL"
    assert len(result.annual_reports) == 1
    assert len(result.quarterly_reports) == 1
    assert result.annual_reports[0].fiscal_date_ending == "2024-09-30"
    assert result.annual_reports[0].reported_currency == "USD"
    assert result.annual_reports[0].data["totalRevenue"] == "383285000000"
    mock_request.assert_called_once_with("INCOME_STATEMENT", symbol="AAPL")


async def test_balance_sheet(mock_request):
    mock_request.return_value = {
        "symbol": "AAPL",
        "annualReports": [
            {
                "fiscalDateEnding": "2024-09-30",
                "reportedCurrency": "USD",
                "totalAssets": "352583000000",
            }
        ],
        "quarterlyReports": [],
    }
    api = FundamentalsAPI(mock_request)
    result = await api.balance_sheet("AAPL")

    assert isinstance(result, FinancialResponse)
    assert result.symbol == "AAPL"
    assert len(result.annual_reports) == 1
    assert result.annual_reports[0].data["totalAssets"] == "352583000000"
    mock_request.assert_called_once_with("BALANCE_SHEET", symbol="AAPL")


async def test_cash_flow(mock_request):
    mock_request.return_value = {
        "symbol": "AAPL",
        "annualReports": [
            {
                "fiscalDateEnding": "2024-09-30",
                "reportedCurrency": "USD",
                "operatingCashflow": "110543000000",
            }
        ],
        "quarterlyReports": [],
    }
    api = FundamentalsAPI(mock_request)
    result = await api.cash_flow("AAPL")

    assert isinstance(result, FinancialResponse)
    assert result.symbol == "AAPL"
    mock_request.assert_called_once_with("CASH_FLOW", symbol="AAPL")


async def test_earnings(mock_request):
    mock_request.return_value = MOCK_EARNINGS
    api = FundamentalsAPI(mock_request)
    result = await api.earnings("AAPL")

    assert isinstance(result, EarningsResponse)
    assert result.symbol == "AAPL"
    assert len(result.annual_earnings) == 1
    assert len(result.quarterly_earnings) == 1

    annual = result.annual_earnings[0]
    assert isinstance(annual, EarningsEntry)
    assert annual.fiscal_date_ending == "2024-09-30"
    assert annual.reported_eps == 6.42

    quarterly = result.quarterly_earnings[0]
    assert quarterly.reported_eps == 1.65
    assert quarterly.estimated_eps == 1.60
    assert quarterly.surprise == 0.05
    assert quarterly.surprise_percentage == 3.125
    mock_request.assert_called_once_with("EARNINGS", symbol="AAPL")


async def test_earnings_estimates(mock_request):
    mock_request.return_value = {
        "symbol": "AAPL",
        "annualEstimates": [
            {
                "fiscalDateEnding": "2025-09-30",
                "numberOfAnalysts": "35",
                "estimatedEPS": "7.20",
                "estimatedRevenue": "420000000000",
            }
        ],
        "quarterlyEstimates": [],
    }
    api = FundamentalsAPI(mock_request)
    result = await api.earnings_estimates("AAPL")

    assert isinstance(result, dict)
    assert result["symbol"] == "AAPL"
    assert len(result["annualEstimates"]) == 1
    mock_request.assert_called_once_with("EARNINGS_ESTIMATES", symbol="AAPL")


async def test_dividends(mock_request):
    mock_request.return_value = MOCK_DIVIDENDS
    api = FundamentalsAPI(mock_request)
    result = await api.dividends("AAPL")

    assert isinstance(result, list)
    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, DividendEntry)
    assert entry.ex_dividend_date == "2024-11-08"
    assert entry.declaration_date == "2024-11-01"
    assert entry.record_date == "2024-11-11"
    assert entry.payment_date == "2024-11-14"
    assert entry.amount == 0.25
    mock_request.assert_called_once_with("DIVIDENDS", symbol="AAPL")


async def test_splits(mock_request):
    mock_request.return_value = MOCK_SPLITS
    api = FundamentalsAPI(mock_request)
    result = await api.splits("AAPL")

    assert isinstance(result, list)
    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, SplitEntry)
    assert entry.effective_date == "2020-08-31"
    assert entry.split_ratio == "4:1"
    mock_request.assert_called_once_with("SPLITS", symbol="AAPL")


async def test_insider_transactions(mock_request):
    mock_request.return_value = MOCK_INSIDER_TRANSACTIONS
    api = FundamentalsAPI(mock_request)
    result = await api.insider_transactions("IBM")

    assert isinstance(result, list)
    assert len(result) == 2
    entry = result[0]
    assert isinstance(entry, InsiderTransaction)
    assert entry.transaction_date == "2026-02-18"
    assert entry.ticker == "IBM"
    assert entry.executive == "KRISHNA, ARVIND"
    assert entry.executive_title == "Director, Chairman, President & CEO"
    assert entry.security_type == "Common Stock"
    assert entry.acquisition_or_disposal == "A"
    assert entry.shares == 5664.0
    assert entry.share_price == 0.0

    disposal = result[1]
    assert disposal.acquisition_or_disposal == "D"
    assert disposal.shares == 2839.0
    assert disposal.share_price == 258.68
    mock_request.assert_called_once_with("INSIDER_TRANSACTIONS", symbol="IBM")


async def test_listing_status(mock_request):
    mock_csv = AsyncMock(
        return_value=[
            {
                "symbol": "AAPL",
                "name": "Apple Inc",
                "exchange": "NASDAQ",
                "assetType": "Stock",
                "ipoDate": "1980-12-12",
                "delistingDate": None,
                "status": "Active",
            }
        ]
    )
    api = FundamentalsAPI(mock_request, request_csv=mock_csv)
    result = await api.listing_status()

    assert isinstance(result, list)
    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, ListingEntry)
    assert entry.symbol == "AAPL"
    assert entry.name == "Apple Inc"
    assert entry.exchange == "NASDAQ"
    assert entry.status == "Active"
    mock_csv.assert_called_once_with("LISTING_STATUS", state="active", date=None)


async def test_earnings_calendar(mock_request):
    mock_csv = AsyncMock(
        return_value=[
            {
                "symbol": "AAPL",
                "reportDate": "2024-01-25",
                "fiscalDateEnding": "2024-12-31",
            }
        ]
    )
    api = FundamentalsAPI(mock_request, request_csv=mock_csv)
    result = await api.earnings_calendar()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["reportDate"] == "2024-01-25"
    mock_csv.assert_called_once_with("EARNINGS_CALENDAR", symbol=None, horizon="3month")


async def test_ipo_calendar(mock_request):
    mock_csv = AsyncMock(
        return_value=[{"symbol": "NEWCO", "name": "New Company Inc", "ipoDate": "2024-03-15"}]
    )
    api = FundamentalsAPI(mock_request, request_csv=mock_csv)
    result = await api.ipo_calendar()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["symbol"] == "NEWCO"
    mock_csv.assert_called_once_with("IPO_CALENDAR")
