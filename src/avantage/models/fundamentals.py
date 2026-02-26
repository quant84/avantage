"""Pydantic models for fundamental data API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CompanyOverview(BaseModel):
    """Company overview with 50+ financial metrics."""

    symbol: str
    name: str | None = None
    description: str | None = None
    exchange: str | None = None
    currency: str | None = None
    country: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_capitalization: float | None = None
    pe_ratio: float | None = None
    peg_ratio: float | None = None
    book_value: float | None = None
    dividend_per_share: float | None = None
    dividend_yield: float | None = None
    eps: float | None = None
    revenue_per_share: float | None = None
    profit_margin: float | None = None
    operating_margin: float | None = None
    return_on_assets: float | None = None
    return_on_equity: float | None = None
    revenue: float | None = None
    gross_profit: float | None = None
    ebitda: float | None = None
    beta: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    moving_average_50: float | None = None
    moving_average_200: float | None = None
    shares_outstanding: float | None = None
    analyst_target_price: float | None = None
    analyst_rating_strong_buy: int | None = None
    analyst_rating_buy: int | None = None
    analyst_rating_hold: int | None = None
    analyst_rating_sell: int | None = None
    analyst_rating_strong_sell: int | None = None


class FinancialReport(BaseModel):
    """A single annual or quarterly financial report (generic container)."""

    fiscal_date_ending: str
    reported_currency: str | None = None
    data: dict[str, Any]


class FinancialResponse(BaseModel):
    """Response containing financial statement data."""

    symbol: str
    annual_reports: list[FinancialReport] = []
    quarterly_reports: list[FinancialReport] = []


class EarningsEntry(BaseModel):
    """Single earnings data point."""

    fiscal_date_ending: str
    reported_eps: float | None = None
    estimated_eps: float | None = None
    surprise: float | None = None
    surprise_percentage: float | None = None


class EarningsResponse(BaseModel):
    """Response containing earnings data."""

    symbol: str
    annual_earnings: list[EarningsEntry] = []
    quarterly_earnings: list[EarningsEntry] = []


class DividendEntry(BaseModel):
    """Single dividend record."""

    ex_dividend_date: str
    declaration_date: str | None = None
    record_date: str | None = None
    payment_date: str | None = None
    amount: float


class SplitEntry(BaseModel):
    """Single stock split record."""

    effective_date: str
    split_ratio: str


class ETFProfile(BaseModel):
    """ETF profile data."""

    symbol: str
    net_assets: float | None = None
    net_expense_ratio: float | None = None
    portfolio_turnover: float | None = None
    dividend_yield: float | None = None
    inception_date: str | None = None
    leveraged: str | None = None
    asset_class: str | None = None
    holdings: list[dict[str, Any]] = []


class InsiderTransaction(BaseModel):
    """Single insider transaction record."""

    transaction_date: str
    ticker: str
    executive: str | None = None
    executive_title: str | None = None
    security_type: str | None = None
    acquisition_or_disposal: str | None = None
    shares: float | None = None
    share_price: float | None = None


class ListingEntry(BaseModel):
    """Active or delisted stock/ETF."""

    symbol: str
    name: str | None = None
    exchange: str | None = None
    asset_type: str | None = None
    ipo_date: str | None = None
    delisting_date: str | None = None
    status: str | None = None
