"""Tests for OptionsAPI."""

from __future__ import annotations

from avantage.api.options import OptionsAPI
from avantage.models.options import OptionsChain, OptionsContract

# ---------------------------------------------------------------------------
# Shared mock data
# ---------------------------------------------------------------------------

_OPTIONS_RESPONSE = {
    "data": [
        {
            "contractID": "AAPL240119C00150000",
            "symbol": "AAPL",
            "expiration": "2024-01-19",
            "strike": "150.00",
            "type": "call",
            "last": "5.20",
            "bid": "5.10",
            "ask": "5.30",
            "volume": "1234",
            "open_interest": "5678",
            "implied_volatility": "0.25",
            "delta": "0.65",
            "gamma": "0.03",
            "theta": "-0.05",
            "vega": "0.15",
            "rho": "0.02",
            "in_the_money": "TRUE",
        },
        {
            "contractID": "AAPL240119P00150000",
            "symbol": "AAPL",
            "expiration": "2024-01-19",
            "strike": "150.00",
            "type": "put",
            "last": "1.80",
            "bid": "1.70",
            "ask": "1.90",
            "volume": "567",
            "open_interest": "2345",
            "implied_volatility": "0.22",
            "delta": "-0.35",
            "gamma": "0.03",
            "theta": "-0.04",
            "vega": "0.14",
            "rho": "-0.01",
            "in_the_money": "FALSE",
        },
    ]
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_chain_returns_options_chain(mock_request):
    mock_request.return_value = _OPTIONS_RESPONSE
    api = OptionsAPI(mock_request)

    result = await api.chain("AAPL")

    mock_request.assert_called_once()
    assert isinstance(result, OptionsChain)
    assert result.symbol == "AAPL"
    assert len(result.contracts) == 2


async def test_chain_contract_fields(mock_request):
    mock_request.return_value = _OPTIONS_RESPONSE
    api = OptionsAPI(mock_request)

    result = await api.chain("AAPL")
    contract = result.contracts[0]

    assert isinstance(contract, OptionsContract)
    assert contract.contract_id == "AAPL240119C00150000"
    assert contract.symbol == "AAPL"
    assert contract.expiration == "2024-01-19"
    assert contract.strike == 150.0
    assert isinstance(contract.strike, float)
    assert contract.type == "call"
    assert contract.last == 5.2
    assert contract.bid == 5.1
    assert contract.ask == 5.3
    assert contract.volume == 1234
    assert contract.open_interest == 5678
    # Greeks parsed as float
    assert contract.implied_volatility == 0.25
    assert contract.delta == 0.65
    assert contract.gamma == 0.03
    assert contract.theta == -0.05
    assert contract.vega == 0.15
    assert contract.rho == 0.02


async def test_chain_in_the_money_parsed_as_bool(mock_request):
    mock_request.return_value = _OPTIONS_RESPONSE
    api = OptionsAPI(mock_request)

    result = await api.chain("AAPL")

    # First contract: in_the_money = "TRUE" -> True
    assert result.contracts[0].in_the_money is True
    assert isinstance(result.contracts[0].in_the_money, bool)

    # Second contract: in_the_money = "FALSE" -> False
    assert result.contracts[1].in_the_money is False
    assert isinstance(result.contracts[1].in_the_money, bool)


async def test_chain_with_require_greeks(mock_request):
    mock_request.return_value = _OPTIONS_RESPONSE
    api = OptionsAPI(mock_request)

    await api.chain("AAPL", require_greeks=True)

    mock_request.assert_called_once_with(
        "REALTIME_OPTIONS",
        symbol="AAPL",
        require_greeks="true",
        contract=None,
        entitlement=None,
    )


async def test_historical_returns_options_chain(mock_request):
    mock_request.return_value = _OPTIONS_RESPONSE
    api = OptionsAPI(mock_request)

    result = await api.historical("AAPL", date="2024-01-19")

    mock_request.assert_called_once()
    assert isinstance(result, OptionsChain)
    assert result.symbol == "AAPL"
    assert len(result.contracts) == 2
    assert result.contracts[0].contract_id == "AAPL240119C00150000"
