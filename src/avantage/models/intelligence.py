"""Pydantic models for Alpha Intelligence API responses."""

from __future__ import annotations

from pydantic import BaseModel


class TickerSentiment(BaseModel):
    """Sentiment score for a specific ticker."""

    ticker: str
    relevance_score: float | None = None
    ticker_sentiment_score: float | None = None
    ticker_sentiment_label: str | None = None


class NewsArticle(BaseModel):
    """News article with sentiment analysis."""

    title: str
    url: str
    time_published: str
    authors: list[str] = []
    summary: str | None = None
    source: str | None = None
    category_within_source: str | None = None
    overall_sentiment_score: float | None = None
    overall_sentiment_label: str | None = None
    ticker_sentiment: list[TickerSentiment] = []


class TopMover(BaseModel):
    """Stock in the top gainers/losers/most active list."""

    ticker: str
    price: float | None = None
    change_amount: float | None = None
    change_percentage: str | None = None
    volume: int | None = None


class TopMoversResponse(BaseModel):
    """Top gainers, losers, and most actively traded."""

    metadata: str | None = None
    last_updated: str | None = None
    top_gainers: list[TopMover] = []
    top_losers: list[TopMover] = []
    most_actively_traded: list[TopMover] = []


class InsiderTransaction(BaseModel):
    """Insider transaction record."""

    ticker: str | None = None
    transaction_type: str | None = None
    shares: float | None = None
    share_price: float | None = None
    transaction_date: str | None = None
    owner_name: str | None = None
    owner_title: str | None = None
