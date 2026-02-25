"""Technical indicator endpoints (50+ indicators)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avantage._parsers import clean_key, parse_float
from avantage.models.indicators import IndicatorResponse, IndicatorValue

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avantage._types import Interval, SeriesType


class IndicatorsAPI:
    """Access all Alpha Vantage technical indicator endpoints."""

    def __init__(self, request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        self._request = request

    # -- Private helper -------------------------------------------------------

    async def _get(
        self,
        function: str,
        symbol: str,
        interval: Interval,
        **params: Any,
    ) -> IndicatorResponse:
        """Fetch and parse a technical indicator response.

        All 50+ indicator endpoints share the same response shape:
        a ``"Meta Data"`` dict and a ``"Technical Analysis: <NAME>"`` dict
        keyed by timestamp.
        """
        data = await self._request(function, symbol=symbol, interval=interval, **params)

        # Parse metadata.
        metadata_key = next((k for k in data if "Meta Data" in k), None)
        metadata: dict[str, str] = {}
        if metadata_key:
            metadata = {clean_key(k): str(v) for k, v in data[metadata_key].items()}

        # Find the "Technical Analysis: ..." key.
        analysis_key = next(
            (k for k in data if k.startswith("Technical Analysis")),
            None,
        )

        entries: list[IndicatorValue] = []
        if analysis_key:
            for timestamp, raw_values in data[analysis_key].items():
                entries.append(
                    IndicatorValue(
                        timestamp=timestamp,
                        values={k: parse_float(v) for k, v in raw_values.items()},
                    )
                )

        return IndicatorResponse(metadata=metadata, data=entries)

    # =========================================================================
    # Overlap Studies
    # =========================================================================

    async def sma(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Simple Moving Average."""
        return await self._get(
            "SMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def ema(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Exponential Moving Average."""
        return await self._get(
            "EMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def wma(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Weighted Moving Average."""
        return await self._get(
            "WMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def dema(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Double Exponential Moving Average."""
        return await self._get(
            "DEMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def tema(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Triple Exponential Moving Average."""
        return await self._get(
            "TEMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def trima(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Triangular Moving Average."""
        return await self._get(
            "TRIMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def kama(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Kaufman Adaptive Moving Average."""
        return await self._get(
            "KAMA",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def t3(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Triple Exponential Moving Average (T3)."""
        return await self._get(
            "T3",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def midpoint(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """MidPoint over period."""
        return await self._get(
            "MIDPOINT",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def mama(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        *,
        fastlimit: float = 0.01,
        slowlimit: float = 0.01,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """MESA Adaptive Moving Average."""
        return await self._get(
            "MAMA",
            symbol,
            interval,
            series_type=series_type,
            fastlimit=fastlimit,
            slowlimit=slowlimit,
            **kwargs,
        )

    async def vwap(
        self,
        symbol: str,
        interval: Interval,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Volume Weighted Average Price."""
        return await self._get("VWAP", symbol, interval, **kwargs)

    async def midprice(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """MidPrice over period."""
        return await self._get(
            "MIDPRICE",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def sar(
        self,
        symbol: str,
        interval: Interval,
        *,
        acceleration: float = 0.01,
        maximum: float = 0.2,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Parabolic SAR."""
        return await self._get(
            "SAR",
            symbol,
            interval,
            acceleration=acceleration,
            maximum=maximum,
            **kwargs,
        )

    async def bbands(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        *,
        nbdevup: int = 2,
        nbdevdn: int = 2,
        matype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Bollinger Bands."""
        return await self._get(
            "BBANDS",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn,
            matype=matype,
            **kwargs,
        )

    # =========================================================================
    # Momentum Indicators
    # =========================================================================

    async def rsi(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Relative Strength Index."""
        return await self._get(
            "RSI",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def stochrsi(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        *,
        fastkperiod: int = 5,
        fastdperiod: int = 3,
        fastdmatype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Stochastic RSI."""
        return await self._get(
            "STOCHRSI",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            fastkperiod=fastkperiod,
            fastdperiod=fastdperiod,
            fastdmatype=fastdmatype,
            **kwargs,
        )

    async def willr(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Williams' %R."""
        return await self._get(
            "WILLR",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def adx(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Average Directional Movement Index."""
        return await self._get(
            "ADX",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def adxr(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """ADX Rating."""
        return await self._get(
            "ADXR",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def apo(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        *,
        fastperiod: int = 12,
        slowperiod: int = 26,
        matype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Absolute Price Oscillator."""
        return await self._get(
            "APO",
            symbol,
            interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            matype=matype,
            **kwargs,
        )

    async def ppo(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        *,
        fastperiod: int = 12,
        slowperiod: int = 26,
        matype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Percentage Price Oscillator."""
        return await self._get(
            "PPO",
            symbol,
            interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            matype=matype,
            **kwargs,
        )

    async def mom(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Momentum."""
        return await self._get(
            "MOM",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def bop(
        self,
        symbol: str,
        interval: Interval,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Balance of Power."""
        return await self._get("BOP", symbol, interval, **kwargs)

    async def cci(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Commodity Channel Index."""
        return await self._get(
            "CCI",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def cmo(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Chande Momentum Oscillator."""
        return await self._get(
            "CMO",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def roc(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Rate of Change."""
        return await self._get(
            "ROC",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def rocr(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Rate of Change Ratio."""
        return await self._get(
            "ROCR",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def aroon(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Aroon."""
        return await self._get(
            "AROON",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def aroonosc(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Aroon Oscillator."""
        return await self._get(
            "AROONOSC",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def mfi(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Money Flow Index."""
        return await self._get(
            "MFI",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def trix(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Triple Smooth EMA."""
        return await self._get(
            "TRIX",
            symbol,
            interval,
            time_period=time_period,
            series_type=series_type,
            **kwargs,
        )

    async def ultosc(
        self,
        symbol: str,
        interval: Interval,
        *,
        timeperiod1: int = 7,
        timeperiod2: int = 14,
        timeperiod3: int = 28,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Ultimate Oscillator."""
        return await self._get(
            "ULTOSC",
            symbol,
            interval,
            timeperiod1=timeperiod1,
            timeperiod2=timeperiod2,
            timeperiod3=timeperiod3,
            **kwargs,
        )

    async def dx(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Directional Movement Index."""
        return await self._get(
            "DX",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def minus_di(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Minus Directional Indicator."""
        return await self._get(
            "MINUS_DI",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def plus_di(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Plus Directional Indicator."""
        return await self._get(
            "PLUS_DI",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def minus_dm(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Minus Directional Movement."""
        return await self._get(
            "MINUS_DM",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def plus_dm(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Plus Directional Movement."""
        return await self._get(
            "PLUS_DM",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    # =========================================================================
    # MACD Family
    # =========================================================================

    async def macd(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        *,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Moving Average Convergence/Divergence."""
        return await self._get(
            "MACD",
            symbol,
            interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            signalperiod=signalperiod,
            **kwargs,
        )

    async def macdext(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        *,
        fastperiod: int = 12,
        fastmatype: int = 0,
        slowperiod: int = 26,
        slowmatype: int = 0,
        signalperiod: int = 9,
        signalmatype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """MACD with controllable MA types."""
        return await self._get(
            "MACDEXT",
            symbol,
            interval,
            series_type=series_type,
            fastperiod=fastperiod,
            fastmatype=fastmatype,
            slowperiod=slowperiod,
            slowmatype=slowmatype,
            signalperiod=signalperiod,
            signalmatype=signalmatype,
            **kwargs,
        )

    # =========================================================================
    # Stochastic Family
    # =========================================================================

    async def stoch(
        self,
        symbol: str,
        interval: Interval,
        *,
        fastkperiod: int = 5,
        slowkperiod: int = 3,
        slowdperiod: int = 3,
        slowkmatype: int = 0,
        slowdmatype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Stochastic (STOCH)."""
        return await self._get(
            "STOCH",
            symbol,
            interval,
            fastkperiod=fastkperiod,
            slowkperiod=slowkperiod,
            slowdperiod=slowdperiod,
            slowkmatype=slowkmatype,
            slowdmatype=slowdmatype,
            **kwargs,
        )

    async def stochf(
        self,
        symbol: str,
        interval: Interval,
        *,
        fastkperiod: int = 5,
        fastdperiod: int = 3,
        fastdmatype: int = 0,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Stochastic Fast (STOCHF)."""
        return await self._get(
            "STOCHF",
            symbol,
            interval,
            fastkperiod=fastkperiod,
            fastdperiod=fastdperiod,
            fastdmatype=fastdmatype,
            **kwargs,
        )

    # =========================================================================
    # Volatility
    # =========================================================================

    async def trange(
        self,
        symbol: str,
        interval: Interval,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """True Range."""
        return await self._get("TRANGE", symbol, interval, **kwargs)

    async def atr(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Average True Range."""
        return await self._get(
            "ATR",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    async def natr(
        self,
        symbol: str,
        interval: Interval,
        time_period: int,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Normalized Average True Range."""
        return await self._get(
            "NATR",
            symbol,
            interval,
            time_period=time_period,
            **kwargs,
        )

    # =========================================================================
    # Volume
    # =========================================================================

    async def ad(
        self,
        symbol: str,
        interval: Interval,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Chaikin A/D Line."""
        return await self._get("AD", symbol, interval, **kwargs)

    async def adosc(
        self,
        symbol: str,
        interval: Interval,
        *,
        fastperiod: int = 3,
        slowperiod: int = 10,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Chaikin A/D Oscillator."""
        return await self._get(
            "ADOSC",
            symbol,
            interval,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            **kwargs,
        )

    async def obv(
        self,
        symbol: str,
        interval: Interval,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """On Balance Volume."""
        return await self._get("OBV", symbol, interval, **kwargs)

    # =========================================================================
    # Hilbert Transform
    # =========================================================================

    async def ht_trendline(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Instantaneous Trendline."""
        return await self._get(
            "HT_TRENDLINE",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )

    async def ht_sine(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Sine Wave."""
        return await self._get(
            "HT_SINE",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )

    async def ht_trendmode(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Trend vs Cycle Mode."""
        return await self._get(
            "HT_TRENDMODE",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )

    async def ht_dcperiod(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Dominant Cycle Period."""
        return await self._get(
            "HT_DCPERIOD",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )

    async def ht_dcphase(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Dominant Cycle Phase."""
        return await self._get(
            "HT_DCPHASE",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )

    async def ht_phasor(
        self,
        symbol: str,
        interval: Interval,
        series_type: SeriesType,
        **kwargs: Any,
    ) -> IndicatorResponse:
        """Hilbert Transform - Phasor Components."""
        return await self._get(
            "HT_PHASOR",
            symbol,
            interval,
            series_type=series_type,
            **kwargs,
        )
