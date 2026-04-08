import logging
import pandas as pd
import numpy as np
from typing import Union, List, Dict, Optional
from .market import history as _history_jq
from ..modules.alpha import compute_rsrs as _compute_rsrs_ak

logger = logging.getLogger(__name__)


def MA(closeArray: Union[pd.Series, np.ndarray, list], timeperiod: int = 30) -> Union[pd.Series, np.ndarray, list]:
    """Simple Moving Average. JQ-compatible."""
    if isinstance(closeArray, pd.Series):
        return closeArray.rolling(window=timeperiod, min_periods=timeperiod).mean()
    series = pd.Series(closeArray)
    res = series.rolling(window=timeperiod, min_periods=timeperiod).mean()
    return res.values if isinstance(closeArray, np.ndarray) else res.tolist()


def EMA(closeArray: Union[pd.Series, np.ndarray, list], timeperiod: int = 30) -> Union[pd.Series, np.ndarray, list]:
    """Exponential Moving Average. JQ-compatible."""
    if isinstance(closeArray, pd.Series):
        return closeArray.ewm(span=timeperiod, adjust=False).mean()
    series = pd.Series(closeArray)
    res = series.ewm(span=timeperiod, adjust=False).mean()
    return res.values if isinstance(closeArray, np.ndarray) else res.tolist()


def MACD(
    security_list: Union[str, List[str]],
    check_date: Optional[str] = None,
    SHORT: int = 12,
    LONG: int = 26,
    MID: int = 9,
    unit: str = "1d",
    include_now: bool = True,
) -> Dict[str, Dict[str, float]]:
    """MACD Indicator. JQ-compatible."""
    if isinstance(security_list, str):
        security_list = [security_list]

    result = {"MACD": {}, "DIFF": {}, "DEA": {}}
    need_count = LONG + MID + 10

    for sec in security_list:
        try:
            df = _history_jq(count=need_count, unit=unit, field="close",
                             security_list=[sec], end_date=check_date)
            if df.empty or sec not in df.columns:
                result["MACD"][sec] = np.nan
                result["DIFF"][sec] = np.nan
                result["DEA"][sec] = np.nan
                continue

            close = df[sec]
            ema_s = close.ewm(span=SHORT, adjust=False).mean()
            ema_l = close.ewm(span=LONG, adjust=False).mean()
            diff = ema_s - ema_l
            dea = diff.ewm(span=MID, adjust=False).mean()
            macd = 2 * (diff - dea)

            result["DIFF"][sec] = float(diff.iloc[-1])
            result["DEA"][sec] = float(dea.iloc[-1])
            result["MACD"][sec] = float(macd.iloc[-1])
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.warning(f"MACD calculation failed for '{sec}': {e}")
            result["MACD"][sec] = np.nan
            result["DIFF"][sec] = np.nan
            result["DEA"][sec] = np.nan

    return result


def KDJ(
    security: Union[str, List[str]],
    check_date: Optional[str] = None,
    unit: str = "1d",
    N: int = 9,
    M1: int = 3,
    M2: int = 3,
    include_now: bool = True,
) -> Dict[str, Dict[str, float]]:
    """KDJ Indicator. JQ-compatible."""
    if isinstance(security, str):
        security = [security]
    result = {"K": {}, "D": {}, "J": {}}

    for sec in security:
        try:
            h = _history_jq(count=N + M1 + M2, unit=unit, field="high",
                            security_list=[sec], end_date=check_date)[sec]
            l = _history_jq(count=N + M1 + M2, unit=unit, field="low",
                            security_list=[sec], end_date=check_date)[sec]
            c = _history_jq(count=N + M1 + M2, unit=unit, field="close",
                            security_list=[sec], end_date=check_date)[sec]

            lowest_l = l.rolling(window=N).min()
            highest_h = h.rolling(window=N).max()
            denom = highest_h - lowest_l
            rsv = ((c - lowest_l) / denom.replace(0, np.nan) * 100).fillna(50)

            k = rsv.ewm(alpha=1 / M1, adjust=False).mean()
            d = k.ewm(alpha=1 / M2, adjust=False).mean()
            j = 3 * k - 2 * d

            result["K"][sec] = float(k.iloc[-1])
            result["D"][sec] = float(d.iloc[-1])
            result["J"][sec] = float(j.iloc[-1])
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.warning(f"KDJ calculation failed for '{sec}': {e}")
            result["K"][sec] = np.nan
            result["D"][sec] = np.nan
            result["J"][sec] = np.nan

    return result


def RSI(price: Union[pd.Series, str], timeperiod: int = 14, check_date: Optional[str] = None) -> Union[pd.Series, float]:
    """Relative Strength Index. JQ-compatible."""
    if isinstance(price, str):
        df = _history_jq(count=timeperiod + 20, unit="1d", field="close",
                         security_list=[price], end_date=check_date)
        if df.empty:
            return np.nan
        close = df[price]
    else:
        close = price if isinstance(price, pd.Series) else pd.Series(price)

    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=timeperiod, min_periods=timeperiod).mean()
    avg_loss = loss.rolling(window=timeperiod, min_periods=timeperiod).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1]) if isinstance(price, str) else rsi


def BOLL(
    security: Union[str, List[str]],
    check_date: Optional[str] = None,
    timeperiod: int = 20,
    nbdevup: int = 2,
    nbdevdn: int = 2,
    unit: str = "1d",
    include_now: bool = True,
) -> Dict[str, Dict[str, float]]:
    """Bollinger Bands. JQ-compatible."""
    if isinstance(security, str):
        security = [security]
    result = {"UPPER": {}, "MIDDLE": {}, "LOWER": {}}

    for sec in security:
        try:
            close = _history_jq(count=timeperiod + 10, unit=unit, field="close",
                                security_list=[sec], end_date=check_date)[sec]
            mid = close.rolling(window=timeperiod, min_periods=timeperiod).mean()
            std = close.rolling(window=timeperiod, min_periods=timeperiod).std()
            result["UPPER"][sec] = float((mid + nbdevup * std).iloc[-1])
            result["MIDDLE"][sec] = float(mid.iloc[-1])
            result["LOWER"][sec] = float((mid - nbdevdn * std).iloc[-1])
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.warning(f"BOLL calculation failed for '{sec}': {e}")
            result["UPPER"][sec] = np.nan
            result["MIDDLE"][sec] = np.nan
            result["LOWER"][sec] = np.nan

    return result


def ATR(
    security: Union[str, List[str]],
    check_date: Optional[str] = None,
    timeperiod: int = 14,
    unit: str = "1d",
    include_now: bool = True,
) -> Dict[str, float]:
    """Average True Range. JQ-compatible."""
    if isinstance(security, str):
        security = [security]
    result = {}

    for sec in security:
        try:
            h = _history_jq(count=timeperiod + 1, unit=unit, field="high",
                            security_list=[sec], end_date=check_date)[sec]
            l = _history_jq(count=timeperiod + 1, unit=unit, field="low",
                            security_list=[sec], end_date=check_date)[sec]
            c = _history_jq(count=timeperiod + 1, unit=unit, field="close",
                            security_list=[sec], end_date=check_date)[sec]

            tr1 = h - l
            tr2 = (h - c.shift(1)).abs()
            tr3 = (l - c.shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=timeperiod, min_periods=timeperiod).mean()
            result[sec] = float(atr.iloc[-1])
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.warning(f"ATR calculation failed for '{sec}': {e}")
            result[sec] = np.nan

    return result


def RSRS(
    security: Union[str, List[str]],
    check_date: Optional[str] = None,
    N: int = 18,
    M: int = 600,
    unit: str = "1d",
) -> Union[float, Dict[str, float]]:
    """RSRS Indicator. JQ-compatible."""
    if isinstance(security, str):
        security = [security]
    result = {}

    for sec in security:
        try:
            h = _history_jq(count=N + M + 50, unit=unit, field="high",
                            security_list=[sec], end_date=check_date)[sec]
            l = _history_jq(count=N + M + 50, unit=unit, field="low",
                            security_list=[sec], end_date=check_date)[sec]
            rsrs_series = _compute_rsrs_ak(h, l, n=N, m=M)
            result[sec] = float(rsrs_series.iloc[-1])
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.warning(f"RSRS calculation failed for '{sec}': {e}")
            result[sec] = np.nan

    if len(security) == 1:
        return result[security[0]]
    return result


__all__ = ["MA", "EMA", "MACD", "KDJ", "RSI", "BOLL", "ATR", "RSRS"]
