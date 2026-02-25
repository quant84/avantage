"""Tests for the CommoditiesAPI."""

from __future__ import annotations

from avantage.api.commodities import CommoditiesAPI
from avantage.models.commodities import CommodityResponse
from avantage.models.common import DataPoint

MOCK_WTI = {
    "name": "WTI Crude Oil Prices",
    "interval": "monthly",
    "unit": "dollars per barrel",
    "data": [
        {"date": "2024-01-01", "value": "75.50"},
        {"date": "2024-02-01", "value": "."},
    ],
}


def _mock_commodity(name: str) -> dict:
    return {
        "name": name,
        "interval": "monthly",
        "unit": "dollars per barrel",
        "data": [{"date": "2024-01-01", "value": "100.00"}],
    }


async def test_wti_returns_commodity_response(mock_request):
    mock_request.return_value = MOCK_WTI
    api = CommoditiesAPI(mock_request)
    result = await api.wti()

    assert isinstance(result, CommodityResponse)
    assert result.name == "WTI Crude Oil Prices"
    assert result.interval == "monthly"
    assert result.unit == "dollars per barrel"
    assert len(result.data) == 2
    mock_request.assert_called_once_with("WTI", interval="monthly")


async def test_wti_data_point_parsed_as_float(mock_request):
    mock_request.return_value = MOCK_WTI
    api = CommoditiesAPI(mock_request)
    result = await api.wti()

    assert isinstance(result.data[0], DataPoint)
    assert result.data[0].date == "2024-01-01"
    assert result.data[0].value == 75.5
    assert isinstance(result.data[0].value, float)


async def test_wti_dot_value_becomes_none(mock_request):
    mock_request.return_value = MOCK_WTI
    api = CommoditiesAPI(mock_request)
    result = await api.wti()

    assert result.data[1].date == "2024-02-01"
    assert result.data[1].value is None


async def test_wti_custom_interval(mock_request):
    mock_request.return_value = {
        "name": "WTI Crude Oil Prices",
        "interval": "daily",
        "unit": "dollars per barrel",
        "data": [{"date": "2024-01-02", "value": "72.00"}],
    }
    api = CommoditiesAPI(mock_request)
    result = await api.wti(interval="daily")

    mock_request.assert_called_once_with("WTI", interval="daily")
    assert result.interval == "daily"


async def test_brent(mock_request):
    mock_request.return_value = _mock_commodity("Brent Crude Oil Prices")
    api = CommoditiesAPI(mock_request)
    result = await api.brent()

    assert isinstance(result, CommodityResponse)
    assert result.name == "Brent Crude Oil Prices"
    assert result.data[0].value == 100.0
    mock_request.assert_called_once_with("BRENT", interval="monthly")


async def test_natural_gas(mock_request):
    mock_request.return_value = _mock_commodity("Henry Hub Natural Gas Spot Price")
    api = CommoditiesAPI(mock_request)
    result = await api.natural_gas()

    assert isinstance(result, CommodityResponse)
    assert result.name == "Henry Hub Natural Gas Spot Price"
    mock_request.assert_called_once_with("NATURAL_GAS", interval="monthly")


async def test_copper(mock_request):
    mock_request.return_value = _mock_commodity("Global Price of Copper")
    api = CommoditiesAPI(mock_request)
    result = await api.copper()

    assert isinstance(result, CommodityResponse)
    assert result.name == "Global Price of Copper"
    mock_request.assert_called_once_with("COPPER", interval="monthly")


async def test_all_commodities(mock_request):
    mock_request.return_value = _mock_commodity("All Commodities Index")
    api = CommoditiesAPI(mock_request)
    result = await api.all_commodities()

    assert isinstance(result, CommodityResponse)
    assert result.name == "All Commodities Index"
    assert len(result.data) == 1
    mock_request.assert_called_once_with("ALL_COMMODITIES", interval="monthly")


async def test_gold_silver_spot(mock_request):
    mock_request.return_value = {
        "symbol": "GOLD",
        "price": "2050.30",
        "updated": "2024-01-02 16:00:00",
    }
    api = CommoditiesAPI(mock_request)
    result = await api.gold_silver_spot("GOLD")

    assert isinstance(result, dict)
    assert result["symbol"] == "GOLD"
    assert result["price"] == "2050.30"
    mock_request.assert_called_once_with("GOLD_SILVER_SPOT", symbol="GOLD")


async def test_gold_silver_history(mock_request):
    mock_request.return_value = {
        "name": "Gold Prices",
        "interval": "monthly",
        "unit": "troy ounce",
        "data": [{"date": "2024-01-01", "value": "2050.00"}],
    }
    api = CommoditiesAPI(mock_request)
    result = await api.gold_silver_history("GOLD")

    assert isinstance(result, CommodityResponse)
    assert result.name == "Gold Prices"
    assert result.data[0].value == 2050.0
    mock_request.assert_called_once_with("GOLD_SILVER_HISTORY", symbol="GOLD", interval="monthly")
