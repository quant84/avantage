"""Tests for the EconomicAPI."""

from __future__ import annotations

from avantage.api.economic import EconomicAPI
from avantage.models.economic import EconomicResponse

MOCK_GDP = {
    "name": "Real Gross Domestic Product",
    "interval": "annual",
    "unit": "billions of dollars",
    "data": [{"date": "2024-01-01", "value": "22345.67"}],
}

MOCK_WITH_DOT = {
    "name": "Test Indicator",
    "interval": "monthly",
    "unit": "percent",
    "data": [
        {"date": "2024-01-01", "value": "3.5"},
        {"date": "2024-02-01", "value": "."},
    ],
}


async def test_real_gdp(mock_request):
    mock_request.return_value = MOCK_GDP
    api = EconomicAPI(mock_request)
    result = await api.real_gdp()

    assert isinstance(result, EconomicResponse)
    assert result.name == "Real Gross Domestic Product"
    assert result.interval == "annual"
    assert result.unit == "billions of dollars"
    assert result.data[0].value == 22345.67
    mock_request.assert_called_once_with("REAL_GDP", interval="annual", maturity=None)


async def test_real_gdp_per_capita(mock_request):
    mock_request.return_value = {
        "name": "Real GDP per Capita",
        "interval": "quarterly",
        "unit": "chained 2012 dollars",
        "data": [{"date": "2024-01-01", "value": "65000.00"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.real_gdp_per_capita()

    assert isinstance(result, EconomicResponse)
    assert result.name == "Real GDP per Capita"
    assert result.data[0].value == 65000.0
    mock_request.assert_called_once_with("REAL_GDP_PER_CAPITA", interval=None, maturity=None)


async def test_treasury_yield_maturity_param(mock_request):
    mock_request.return_value = {
        "name": "Treasury Yield",
        "interval": "monthly",
        "unit": "percent",
        "data": [{"date": "2024-01-01", "value": "4.25"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.treasury_yield(maturity="2year")

    mock_request.assert_called_once_with("TREASURY_YIELD", interval="monthly", maturity="2year")
    assert result.data[0].value == 4.25


async def test_federal_funds_rate(mock_request):
    mock_request.return_value = {
        "name": "Federal Funds Rate",
        "interval": "monthly",
        "unit": "percent",
        "data": [{"date": "2024-01-01", "value": "5.33"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.federal_funds_rate()

    assert isinstance(result, EconomicResponse)
    assert result.data[0].value == 5.33
    mock_request.assert_called_once_with("FEDERAL_FUNDS_RATE", interval="monthly", maturity=None)


async def test_cpi(mock_request):
    mock_request.return_value = {
        "name": "Consumer Price Index",
        "interval": "monthly",
        "unit": "index 1982-1984=100",
        "data": [{"date": "2024-01-01", "value": "308.42"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.cpi()

    assert isinstance(result, EconomicResponse)
    assert result.data[0].value == 308.42
    mock_request.assert_called_once_with("CPI", interval="monthly", maturity=None)


async def test_inflation(mock_request):
    mock_request.return_value = {
        "name": "Inflation - US Consumer Prices",
        "interval": "annual",
        "unit": "percent",
        "data": [{"date": "2024-01-01", "value": "3.1"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.inflation()

    assert isinstance(result, EconomicResponse)
    assert result.data[0].value == 3.1
    mock_request.assert_called_once_with("INFLATION", interval=None, maturity=None)


async def test_unemployment(mock_request):
    mock_request.return_value = {
        "name": "Unemployment Rate",
        "interval": "monthly",
        "unit": "percent",
        "data": [{"date": "2024-01-01", "value": "3.7"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.unemployment()

    assert isinstance(result, EconomicResponse)
    assert result.data[0].value == 3.7
    mock_request.assert_called_once_with("UNEMPLOYMENT", interval=None, maturity=None)


async def test_nonfarm_payroll(mock_request):
    mock_request.return_value = {
        "name": "Total Nonfarm Payroll",
        "interval": "monthly",
        "unit": "thousands of persons",
        "data": [{"date": "2024-01-01", "value": "157000"}],
    }
    api = EconomicAPI(mock_request)
    result = await api.nonfarm_payroll()

    assert isinstance(result, EconomicResponse)
    assert result.data[0].value == 157000.0
    mock_request.assert_called_once_with("NONFARM_PAYROLL", interval=None, maturity=None)


async def test_dot_value_becomes_none(mock_request):
    mock_request.return_value = MOCK_WITH_DOT
    api = EconomicAPI(mock_request)
    result = await api.real_gdp()

    assert result.data[0].value == 3.5
    assert result.data[1].value is None
