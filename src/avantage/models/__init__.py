"""Pydantic models for Alpha Vantage API responses."""

from __future__ import annotations

# Commodities models
from avantage.models.commodities import CommodityResponse

# Common models
from avantage.models.common import DataPoint, TimeSeriesEntry, TimeSeriesResponse

# Crypto models
from avantage.models.crypto import CryptoDataPoint

# Economic models
from avantage.models.economic import EconomicResponse

# Equity models
from avantage.models.equity import (
    BulkQuoteEntry,
    GlobalQuote,
    MarketStatus,
    SymbolMatch,
)

# Forex models
from avantage.models.forex import ExchangeRate, FXDataPoint

# Fundamentals models
from avantage.models.fundamentals import (
    CompanyOverview,
    DividendEntry,
    EarningsEntry,
    EarningsResponse,
    ETFProfile,
    FinancialReport,
    FinancialResponse,
    ListingEntry,
    SplitEntry,
)

# Indicators models
from avantage.models.indicators import IndicatorResponse, IndicatorValue

# Intelligence models
from avantage.models.intelligence import (
    InsiderTransaction,
    NewsArticle,
    TickerSentiment,
    TopMover,
    TopMoversResponse,
)

# Options models
from avantage.models.options import OptionsChain, OptionsContract

__all__ = [
    # Common
    "DataPoint",
    "TimeSeriesEntry",
    "TimeSeriesResponse",
    # Equity
    "BulkQuoteEntry",
    "GlobalQuote",
    "MarketStatus",
    "SymbolMatch",
    # Forex
    "ExchangeRate",
    "FXDataPoint",
    # Crypto
    "CryptoDataPoint",
    # Commodities
    "CommodityResponse",
    # Economic
    "EconomicResponse",
    # Indicators
    "IndicatorResponse",
    "IndicatorValue",
    # Options
    "OptionsChain",
    "OptionsContract",
    # Fundamentals
    "CompanyOverview",
    "DividendEntry",
    "EarningsEntry",
    "EarningsResponse",
    "ETFProfile",
    "FinancialReport",
    "FinancialResponse",
    "ListingEntry",
    "SplitEntry",
    # Intelligence
    "InsiderTransaction",
    "NewsArticle",
    "TickerSentiment",
    "TopMover",
    "TopMoversResponse",
]
