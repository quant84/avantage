"""Alpha Intelligence endpoints (news sentiment, top movers, transcripts, insider)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import parse_float, parse_int
from avantage.models.intelligence import (
    InsiderTransaction,
    NewsArticle,
    TickerSentiment,
    TopMover,
    TopMoversResponse,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class IntelligenceAPI:
    """Access Alpha Intelligence: news sentiment, top movers, transcripts, and insider data."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Endpoints ------------------------------------------------------------

    async def news_sentiment(
        self,
        *,
        tickers: str | None = None,
        topics: str | None = None,
        time_from: str | None = None,
        time_to: str | None = None,
        sort: str = "LATEST",
        limit: int = 50,
    ) -> list[NewsArticle]:
        """Fetch news articles with sentiment analysis.

        Args:
            tickers: Comma-separated ticker symbols to filter by.
            topics: Comma-separated topics to filter by.
            time_from: Start time in ``YYYYMMDDTHHMM`` format.
            time_to: End time in ``YYYYMMDDTHHMM`` format.
            sort: Sort order (``"LATEST"``, ``"EARLIEST"``, ``"RELEVANCE"``).
            limit: Maximum number of articles to return.
        """
        data = await self._request(
            "NEWS_SENTIMENT",
            tickers=tickers,
            topics=topics,
            time_from=time_from,
            time_to=time_to,
            sort=sort,
            limit=limit,
        )
        articles: list[NewsArticle] = []
        for item in data.get("feed", []):
            ticker_sentiments: list[TickerSentiment] = []
            for ts in item.get("ticker_sentiment", []):
                ticker_sentiments.append(
                    TickerSentiment(
                        ticker=ts.get("ticker", ""),
                        relevance_score=parse_float(ts.get("relevance_score")),
                        ticker_sentiment_score=parse_float(ts.get("ticker_sentiment_score")),
                        ticker_sentiment_label=ts.get("ticker_sentiment_label"),
                    )
                )
            articles.append(
                NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    time_published=item.get("time_published", ""),
                    authors=item.get("authors", []),
                    summary=item.get("summary"),
                    source=item.get("source"),
                    category_within_source=item.get("category_within_source"),
                    overall_sentiment_score=parse_float(item.get("overall_sentiment_score")),
                    overall_sentiment_label=item.get("overall_sentiment_label"),
                    ticker_sentiment=ticker_sentiments,
                )
            )
        return articles

    async def top_movers(self) -> TopMoversResponse:
        """Fetch top gainers, losers, and most actively traded stocks."""
        data = await self._request("TOP_GAINERS_LOSERS")

        def _parse_movers(items: list[dict[str, Any]]) -> list[TopMover]:
            return [
                TopMover(
                    ticker=item.get("ticker", ""),
                    price=parse_float(item.get("price")),
                    change_amount=parse_float(item.get("change_amount")),
                    change_percentage=item.get("change_percentage"),
                    volume=parse_int(item.get("volume")),
                )
                for item in items
            ]

        return TopMoversResponse(
            metadata=data.get("metadata"),
            last_updated=data.get("last_updated"),
            top_gainers=_parse_movers(data.get("top_gainers", [])),
            top_losers=_parse_movers(data.get("top_losers", [])),
            most_actively_traded=_parse_movers(data.get("most_actively_traded", [])),
        )

    async def earnings_call_transcript(
        self,
        symbol: str,
        quarter: str,
    ) -> dict[str, Any]:
        """Fetch an earnings call transcript.

        Args:
            symbol: Ticker symbol (e.g. ``"IBM"``).
            quarter: Fiscal quarter in ``YYYYQN`` format (e.g. ``"2024Q1"``).
                Supports quarters since ``"2010Q1"``.

        Returns:
            Raw transcript data (structure varies by endpoint response).
        """
        return await self._request(
            "EARNINGS_CALL_TRANSCRIPT",
            symbol=symbol,
            quarter=quarter,
        )

    async def insider_transactions(self, symbol: str) -> list[InsiderTransaction]:
        """Fetch insider transactions for a symbol.

        Args:
            symbol: Ticker symbol.
        """
        data = await self._request("INSIDER_TRANSACTIONS", symbol=symbol)
        entries: list[InsiderTransaction] = []
        for item in data.get("data", []):
            entries.append(
                InsiderTransaction(
                    ticker=item.get("ticker"),
                    transaction_type=item.get("transaction_type"),
                    shares=parse_float(item.get("shares")),
                    share_price=parse_float(item.get("share_price")),
                    transaction_date=item.get("transaction_date"),
                    owner_name=item.get("owner_name"),
                    owner_title=item.get("owner_title"),
                )
            )
        return entries
