"""Fundamental data endpoints (financials, earnings, dividends, etc.)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import parse_float, parse_int
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

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class FundamentalsAPI:
    """Access fundamental data: financials, earnings, dividends, splits, and listings."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helpers ------------------------------------------------------

    @staticmethod
    def _parse_financial(data: dict[str, Any], symbol: str) -> FinancialResponse:
        """Parse an income statement, balance sheet, or cash flow response."""
        annual: list[FinancialReport] = []
        for report in data.get("annualReports", []):
            report_copy = dict(report)
            fiscal_date = report_copy.pop("fiscalDateEnding", "")
            currency = report_copy.pop("reportedCurrency", None)
            annual.append(
                FinancialReport(
                    fiscal_date_ending=fiscal_date,
                    reported_currency=currency,
                    data=report_copy,
                )
            )

        quarterly: list[FinancialReport] = []
        for report in data.get("quarterlyReports", []):
            report_copy = dict(report)
            fiscal_date = report_copy.pop("fiscalDateEnding", "")
            currency = report_copy.pop("reportedCurrency", None)
            quarterly.append(
                FinancialReport(
                    fiscal_date_ending=fiscal_date,
                    reported_currency=currency,
                    data=report_copy,
                )
            )

        return FinancialResponse(
            symbol=symbol,
            annual_reports=annual,
            quarterly_reports=quarterly,
        )

    # -- Endpoints ------------------------------------------------------------

    async def overview(self, symbol: str) -> CompanyOverview:
        """Fetch company overview with 50+ financial metrics.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``).
        """
        data = await self._request("OVERVIEW", symbol=symbol)
        return CompanyOverview(
            symbol=data.get("Symbol", symbol),
            name=data.get("Name"),
            description=data.get("Description"),
            exchange=data.get("Exchange"),
            currency=data.get("Currency"),
            country=data.get("Country"),
            sector=data.get("Sector"),
            industry=data.get("Industry"),
            market_capitalization=parse_float(data.get("MarketCapitalization")),
            pe_ratio=parse_float(data.get("PERatio")),
            peg_ratio=parse_float(data.get("PEGRatio")),
            book_value=parse_float(data.get("BookValue")),
            dividend_per_share=parse_float(data.get("DividendPerShare")),
            dividend_yield=parse_float(data.get("DividendYield")),
            eps=parse_float(data.get("EPS")),
            revenue_per_share=parse_float(data.get("RevenuePerShareTTM")),
            profit_margin=parse_float(data.get("ProfitMargin")),
            operating_margin=parse_float(data.get("OperatingMarginTTM")),
            return_on_assets=parse_float(data.get("ReturnOnAssetsTTM")),
            return_on_equity=parse_float(data.get("ReturnOnEquityTTM")),
            revenue=parse_float(data.get("RevenueTTM")),
            gross_profit=parse_float(data.get("GrossProfitTTM")),
            ebitda=parse_float(data.get("EBITDA")),
            beta=parse_float(data.get("Beta")),
            week_52_high=parse_float(data.get("52WeekHigh")),
            week_52_low=parse_float(data.get("52WeekLow")),
            moving_average_50=parse_float(data.get("50DayMovingAverage")),
            moving_average_200=parse_float(data.get("200DayMovingAverage")),
            shares_outstanding=parse_float(data.get("SharesOutstanding")),
            analyst_target_price=parse_float(data.get("AnalystTargetPrice")),
            analyst_rating_strong_buy=parse_int(data.get("AnalystRatingStrongBuy")),
            analyst_rating_buy=parse_int(data.get("AnalystRatingBuy")),
            analyst_rating_hold=parse_int(data.get("AnalystRatingHold")),
            analyst_rating_sell=parse_int(data.get("AnalystRatingSell")),
            analyst_rating_strong_sell=parse_int(data.get("AnalystRatingStrongSell")),
        )

    async def etf_profile(self, symbol: str) -> ETFProfile:
        """Fetch ETF profile data.

        Args:
            symbol: ETF ticker symbol (e.g. ``"SPY"``).
        """
        data = await self._request("ETF_PROFILE", symbol=symbol)
        return ETFProfile(
            symbol=data.get("Symbol", symbol),
            net_assets=parse_float(data.get("NetAssets")),
            net_expense_ratio=parse_float(data.get("NetExpenseRatio")),
            portfolio_turnover=parse_float(data.get("PortfolioTurnover")),
            dividend_yield=parse_float(data.get("DividendYield")),
            inception_date=data.get("InceptionDate"),
            leveraged=data.get("Leveraged"),
            asset_class=data.get("AssetClass"),
            holdings=data.get("Holdings", []),
        )

    async def income_statement(self, symbol: str) -> FinancialResponse:
        """Fetch annual and quarterly income statements.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("INCOME_STATEMENT", symbol=symbol)
        return self._parse_financial(data, data.get("symbol", symbol))

    async def balance_sheet(self, symbol: str) -> FinancialResponse:
        """Fetch annual and quarterly balance sheets.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("BALANCE_SHEET", symbol=symbol)
        return self._parse_financial(data, data.get("symbol", symbol))

    async def cash_flow(self, symbol: str) -> FinancialResponse:
        """Fetch annual and quarterly cash flow statements.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("CASH_FLOW", symbol=symbol)
        return self._parse_financial(data, data.get("symbol", symbol))

    async def earnings(self, symbol: str) -> EarningsResponse:
        """Fetch annual and quarterly earnings data.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("EARNINGS", symbol=symbol)

        annual: list[EarningsEntry] = []
        for entry in data.get("annualEarnings", []):
            annual.append(
                EarningsEntry(
                    fiscal_date_ending=entry.get("fiscalDateEnding", ""),
                    reported_eps=parse_float(entry.get("reportedEPS")),
                )
            )

        quarterly: list[EarningsEntry] = []
        for entry in data.get("quarterlyEarnings", []):
            quarterly.append(
                EarningsEntry(
                    fiscal_date_ending=entry.get("fiscalDateEnding", ""),
                    reported_eps=parse_float(entry.get("reportedEPS")),
                    estimated_eps=parse_float(entry.get("estimatedEPS")),
                    surprise=parse_float(entry.get("surprise")),
                    surprise_percentage=parse_float(entry.get("surprisePercentage")),
                )
            )

        return EarningsResponse(
            symbol=data.get("symbol", symbol),
            annual_earnings=annual,
            quarterly_earnings=quarterly,
        )

    async def earnings_estimates(self, symbol: str) -> dict[str, Any]:
        """Fetch annual and quarterly EPS and revenue estimates with analyst data.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``).

        Returns:
            Raw earnings estimates data including analyst count and revision history.
        """
        return await self._request("EARNINGS_ESTIMATES", symbol=symbol)

    async def dividends(self, symbol: str) -> list[DividendEntry]:
        """Fetch historical dividend data.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("DIVIDENDS", symbol=symbol)
        entries: list[DividendEntry] = []
        for item in data.get("data", []):
            entries.append(
                DividendEntry(
                    ex_dividend_date=item.get("ex_dividend_date", ""),
                    declaration_date=item.get("declaration_date"),
                    record_date=item.get("record_date"),
                    payment_date=item.get("payment_date"),
                    amount=float(item.get("amount", 0)),
                )
            )
        return entries

    async def splits(self, symbol: str) -> list[SplitEntry]:
        """Fetch historical stock split data.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("SPLITS", symbol=symbol)
        entries: list[SplitEntry] = []
        for item in data.get("data", []):
            entries.append(
                SplitEntry(
                    effective_date=item.get("effective_date", ""),
                    split_ratio=item.get("split_ratio", ""),
                )
            )
        return entries

    async def listing_status(
        self,
        *,
        state: str = "active",
        date: str | None = None,
    ) -> list[ListingEntry]:
        """Fetch active or delisted ticker listings.

        Args:
            state: ``"active"`` or ``"delisted"``.
            date: Optional date in ``YYYY-MM-DD`` format.
        """
        data = await self._request("LISTING_STATUS", state=state, date=date)
        raw_list = data.get("data", data) if isinstance(data, dict) else data
        entries: list[ListingEntry] = []
        if isinstance(raw_list, list):
            for item in raw_list:
                entries.append(
                    ListingEntry(
                        symbol=item.get("symbol", ""),
                        name=item.get("name"),
                        exchange=item.get("exchange"),
                        asset_type=item.get("assetType"),
                        ipo_date=item.get("ipoDate"),
                        delisting_date=item.get("delistingDate"),
                        status=item.get("status"),
                    )
                )
        return entries

    @staticmethod
    def _extract_list(data: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
        """Extract a list of entries from a raw calendar response."""
        if isinstance(data, dict):
            entries = data.get("data")
            if isinstance(entries, list):
                return entries
            return [data] if data else []
        if isinstance(data, list):
            return data
        return []

    async def earnings_calendar(
        self,
        *,
        symbol: str | None = None,
        horizon: str = "3month",
    ) -> list[dict[str, Any]]:
        """Fetch upcoming earnings announcements.

        Args:
            symbol: Optional ticker to filter by.
            horizon: ``"3month"``, ``"6month"``, or ``"12month"``.
        """
        data = await self._request("EARNINGS_CALENDAR", symbol=symbol, horizon=horizon)
        return self._extract_list(data)

    async def ipo_calendar(self) -> list[dict[str, Any]]:
        """Fetch upcoming IPO events."""
        data = await self._request("IPO_CALENDAR")
        return self._extract_list(data)
