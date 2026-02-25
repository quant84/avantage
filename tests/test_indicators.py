"""Tests for the IndicatorsAPI."""

from __future__ import annotations

from avantage.api.indicators import IndicatorsAPI
from avantage.models.indicators import IndicatorResponse, IndicatorValue

MOCK_SMA = {
    "Meta Data": {
        "1. Symbol": "AAPL",
        "2. Indicator": "Simple Moving Average (SMA)",
        "3. Last Refreshed": "2024-01-02",
        "4. Interval": "daily",
        "5. Time Period": "20",
        "6. Series Type": "close",
    },
    "Technical Analysis: SMA": {
        "2024-01-02": {"SMA": "188.52"},
        "2024-01-01": {"SMA": "187.30"},
    },
}

MOCK_MACD = {
    "Meta Data": {"1. Symbol": "AAPL"},
    "Technical Analysis: MACD": {
        "2024-01-02": {
            "MACD": "1.23",
            "MACD_Signal": "0.98",
            "MACD_Hist": "0.25",
        }
    },
}

MOCK_BBANDS = {
    "Meta Data": {"1. Symbol": "AAPL"},
    "Technical Analysis: BBANDS": {
        "2024-01-02": {
            "Real Upper Band": "195.00",
            "Real Middle Band": "188.52",
            "Real Lower Band": "182.04",
        }
    },
}

MOCK_STOCH = {
    "Meta Data": {"1. Symbol": "AAPL"},
    "Technical Analysis: STOCH": {"2024-01-02": {"SlowK": "75.50", "SlowD": "72.30"}},
}

MOCK_SINGLE = {
    "Meta Data": {"1. Symbol": "AAPL"},
    "Technical Analysis: RSI": {"2024-01-02": {"RSI": "65.42"}},
}


async def test_sma(mock_request):
    mock_request.return_value = MOCK_SMA
    api = IndicatorsAPI(mock_request)
    result = await api.sma("AAPL", "daily", 20, "close")

    assert isinstance(result, IndicatorResponse)
    assert len(result.data) == 2
    assert result.data[0].timestamp == "2024-01-02"
    assert result.data[0].values["SMA"] == 188.52
    assert result.data[1].values["SMA"] == 187.30
    mock_request.assert_called_once_with(
        "SMA", symbol="AAPL", interval="daily", time_period=20, series_type="close"
    )


async def test_sma_metadata_parsed(mock_request):
    mock_request.return_value = MOCK_SMA
    api = IndicatorsAPI(mock_request)
    result = await api.sma("AAPL", "daily", 20, "close")

    # clean_key strips "N. " prefixes from Alpha Vantage keys
    assert result.metadata["Symbol"] == "AAPL"
    assert result.metadata["Indicator"] == "Simple Moving Average (SMA)"
    assert result.metadata["Interval"] == "daily"


async def test_ema(mock_request):
    mock_data = {
        "Meta Data": {"1. Symbol": "AAPL"},
        "Technical Analysis: EMA": {"2024-01-02": {"EMA": "189.10"}},
    }
    mock_request.return_value = mock_data
    api = IndicatorsAPI(mock_request)
    result = await api.ema("AAPL", "daily", 20, "close")

    assert isinstance(result, IndicatorResponse)
    assert result.data[0].values["EMA"] == 189.10
    mock_request.assert_called_once_with(
        "EMA", symbol="AAPL", interval="daily", time_period=20, series_type="close"
    )


async def test_rsi(mock_request):
    mock_request.return_value = MOCK_SINGLE
    api = IndicatorsAPI(mock_request)
    result = await api.rsi("AAPL", "daily", 14, "close")

    assert isinstance(result, IndicatorResponse)
    assert result.data[0].values["RSI"] == 65.42
    mock_request.assert_called_once_with(
        "RSI", symbol="AAPL", interval="daily", time_period=14, series_type="close"
    )


async def test_macd_multi_value(mock_request):
    mock_request.return_value = MOCK_MACD
    api = IndicatorsAPI(mock_request)
    result = await api.macd("AAPL", "daily", "close")

    assert isinstance(result, IndicatorResponse)
    entry = result.data[0]
    assert isinstance(entry, IndicatorValue)
    assert entry.values["MACD"] == 1.23
    assert entry.values["MACD_Signal"] == 0.98
    assert entry.values["MACD_Hist"] == 0.25
    mock_request.assert_called_once_with(
        "MACD",
        symbol="AAPL",
        interval="daily",
        series_type="close",
        fastperiod=12,
        slowperiod=26,
        signalperiod=9,
    )


async def test_bbands_multi_value(mock_request):
    mock_request.return_value = MOCK_BBANDS
    api = IndicatorsAPI(mock_request)
    result = await api.bbands("AAPL", "daily", 20, "close")

    entry = result.data[0]
    assert entry.values["Real Upper Band"] == 195.00
    assert entry.values["Real Middle Band"] == 188.52
    assert entry.values["Real Lower Band"] == 182.04


async def test_stoch_multi_value(mock_request):
    mock_request.return_value = MOCK_STOCH
    api = IndicatorsAPI(mock_request)
    result = await api.stoch("AAPL", "daily")

    entry = result.data[0]
    assert entry.values["SlowK"] == 75.50
    assert entry.values["SlowD"] == 72.30
    mock_request.assert_called_once_with(
        "STOCH",
        symbol="AAPL",
        interval="daily",
        fastkperiod=5,
        slowkperiod=3,
        slowdperiod=3,
        slowkmatype=0,
        slowdmatype=0,
    )


async def test_adx_time_period_only(mock_request):
    mock_data = {
        "Meta Data": {"1. Symbol": "AAPL"},
        "Technical Analysis: ADX": {"2024-01-02": {"ADX": "25.30"}},
    }
    mock_request.return_value = mock_data
    api = IndicatorsAPI(mock_request)
    result = await api.adx("AAPL", "daily", 14)

    assert result.data[0].values["ADX"] == 25.30
    mock_request.assert_called_once_with("ADX", symbol="AAPL", interval="daily", time_period=14)


async def test_obv_symbol_interval_only(mock_request):
    mock_data = {
        "Meta Data": {"1. Symbol": "AAPL"},
        "Technical Analysis: OBV": {"2024-01-02": {"OBV": "5000000.0000"}},
    }
    mock_request.return_value = mock_data
    api = IndicatorsAPI(mock_request)
    result = await api.obv("AAPL", "daily")

    assert result.data[0].values["OBV"] == 5000000.0
    mock_request.assert_called_once_with("OBV", symbol="AAPL", interval="daily")


async def test_ht_trendline_series_type(mock_request):
    mock_data = {
        "Meta Data": {"1. Symbol": "AAPL"},
        "Technical Analysis: HT_TRENDLINE": {"2024-01-02": {"HT_TRENDLINE": "188.00"}},
    }
    mock_request.return_value = mock_data
    api = IndicatorsAPI(mock_request)
    result = await api.ht_trendline("AAPL", "daily", "close")

    assert result.data[0].values["HT_TRENDLINE"] == 188.0
    mock_request.assert_called_once_with(
        "HT_TRENDLINE", symbol="AAPL", interval="daily", series_type="close"
    )


async def test_params_forwarded_correctly(mock_request):
    mock_request.return_value = MOCK_SMA
    api = IndicatorsAPI(mock_request)
    await api.sma("MSFT", "weekly", 50, "open")

    mock_request.assert_called_once_with(
        "SMA", symbol="MSFT", interval="weekly", time_period=50, series_type="open"
    )
