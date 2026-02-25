"""Tests for the IntelligenceAPI."""

from __future__ import annotations

from avantage.api.intelligence import IntelligenceAPI
from avantage.models.intelligence import (
    InsiderTransaction,
    NewsArticle,
    TickerSentiment,
    TopMover,
    TopMoversResponse,
)

MOCK_NEWS = {
    "feed": [
        {
            "title": "Apple Q4 Earnings",
            "url": "https://example.com",
            "time_published": "20240102T120000",
            "authors": ["John"],
            "summary": "Apple reported...",
            "source": "Reuters",
            "overall_sentiment_score": "0.25",
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.95",
                    "ticker_sentiment_score": "0.30",
                    "ticker_sentiment_label": "Somewhat-Bullish",
                }
            ],
        }
    ]
}

MOCK_TOP_MOVERS = {
    "metadata": "Top gainers, losers, and most actively traded",
    "last_updated": "2024-01-02",
    "top_gainers": [
        {
            "ticker": "XYZ",
            "price": "10.00",
            "change_amount": "2.00",
            "change_percentage": "25.00%",
            "volume": "5000000",
        }
    ],
    "top_losers": [
        {
            "ticker": "ABC",
            "price": "5.00",
            "change_amount": "-1.00",
            "change_percentage": "-16.67%",
            "volume": "3000000",
        }
    ],
    "most_actively_traded": [
        {
            "ticker": "AAPL",
            "price": "188.00",
            "change_amount": "3.00",
            "change_percentage": "1.62%",
            "volume": "80000000",
        }
    ],
}


async def test_news_sentiment(mock_request):
    mock_request.return_value = MOCK_NEWS
    api = IntelligenceAPI(mock_request)
    result = await api.news_sentiment(tickers="AAPL")

    assert isinstance(result, list)
    assert len(result) == 1
    article = result[0]
    assert isinstance(article, NewsArticle)
    assert article.title == "Apple Q4 Earnings"
    assert article.url == "https://example.com"
    assert article.time_published == "20240102T120000"
    assert article.authors == ["John"]
    assert article.summary == "Apple reported..."
    assert article.source == "Reuters"
    assert article.overall_sentiment_score == 0.25
    assert article.overall_sentiment_label == "Somewhat-Bullish"
    mock_request.assert_called_once_with(
        "NEWS_SENTIMENT",
        tickers="AAPL",
        topics=None,
        time_from=None,
        time_to=None,
        sort="LATEST",
        limit=50,
    )


async def test_news_sentiment_ticker_sentiment_parsed(mock_request):
    mock_request.return_value = MOCK_NEWS
    api = IntelligenceAPI(mock_request)
    result = await api.news_sentiment()

    article = result[0]
    assert len(article.ticker_sentiment) == 1
    ts = article.ticker_sentiment[0]
    assert isinstance(ts, TickerSentiment)
    assert ts.ticker == "AAPL"
    assert ts.relevance_score == 0.95
    assert ts.ticker_sentiment_score == 0.30
    assert ts.ticker_sentiment_label == "Somewhat-Bullish"


async def test_top_movers(mock_request):
    mock_request.return_value = MOCK_TOP_MOVERS
    api = IntelligenceAPI(mock_request)
    result = await api.top_movers()

    assert isinstance(result, TopMoversResponse)
    assert result.metadata == "Top gainers, losers, and most actively traded"
    assert result.last_updated == "2024-01-02"

    assert len(result.top_gainers) == 1
    gainer = result.top_gainers[0]
    assert isinstance(gainer, TopMover)
    assert gainer.ticker == "XYZ"
    assert gainer.price == 10.0
    assert gainer.change_amount == 2.0
    assert gainer.change_percentage == "25.00%"
    assert gainer.volume == 5000000

    assert len(result.top_losers) == 1
    assert result.top_losers[0].ticker == "ABC"
    assert result.top_losers[0].change_amount == -1.0

    assert len(result.most_actively_traded) == 1
    assert result.most_actively_traded[0].ticker == "AAPL"
    assert result.most_actively_traded[0].volume == 80000000

    mock_request.assert_called_once_with("TOP_GAINERS_LOSERS")


async def test_earnings_call_transcript(mock_request):
    mock_response = {"symbol": "AAPL", "transcript": "Good afternoon..."}
    mock_request.return_value = mock_response
    api = IntelligenceAPI(mock_request)
    result = await api.earnings_call_transcript("AAPL", "2024Q4")

    assert isinstance(result, dict)
    assert result["symbol"] == "AAPL"
    assert result["transcript"] == "Good afternoon..."
    mock_request.assert_called_once_with(
        "EARNINGS_CALL_TRANSCRIPT", symbol="AAPL", quarter="2024Q4"
    )


async def test_insider_transactions(mock_request):
    mock_request.return_value = {
        "data": [
            {
                "ticker": "AAPL",
                "transaction_type": "S-Sale",
                "shares": "50000",
                "share_price": "188.50",
                "transaction_date": "2024-01-02",
                "owner_name": "Tim Cook",
                "owner_title": "CEO",
            }
        ]
    }
    api = IntelligenceAPI(mock_request)
    result = await api.insider_transactions("AAPL")

    assert isinstance(result, list)
    assert len(result) == 1
    tx = result[0]
    assert isinstance(tx, InsiderTransaction)
    assert tx.ticker == "AAPL"
    assert tx.transaction_type == "S-Sale"
    assert tx.shares == 50000.0
    assert tx.share_price == 188.50
    assert tx.transaction_date == "2024-01-02"
    assert tx.owner_name == "Tim Cook"
    assert tx.owner_title == "CEO"
    mock_request.assert_called_once_with("INSIDER_TRANSACTIONS", symbol="AAPL")
