import akshare as ak
import pandas as pd

from ..cache import cache
from ..utils import convert_xieqiu_symbol
from .base import RealtimeDataProvider


class XueQiuRealtime(RealtimeDataProvider):
    @cache(
        "realtime_cache",
        key=lambda self: f"xueqiu_{self.symbol}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """获取雪球实时行情数据

        Args:
            symbol: 股票代码 ("600000")

        Returns:
            pd.DataFrame with columns:
            - symbol: 股票代码
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - timestamp: 时间戳
            - volume: 成交量(手)
            - amount: 成交额(元)
            - open: 今开
            - high: 最高
            - low: 最低
            - prev_close: 昨收
        
        Raises:
            RuntimeError: When the upstream API returns unexpected format
        """
        try:
            raw_df = ak.stock_individual_spot_xq(symbol=convert_xieqiu_symbol(self.symbol))
        except KeyError as e:
            raise RuntimeError(
                f"Xueqiu API returned unexpected response format. "
                f"The API may have changed or be temporarily unavailable. Error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch data from Xueqiu API. "
                f"The service may be unavailable. Error: {e}"
            ) from e

        # Check if DataFrame is empty or has unexpected structure
        if raw_df.empty:
            raise RuntimeError(
                f"Xueqiu API returned empty data for symbol {self.symbol}. "
                f"The stock may not exist or data is temporarily unavailable."
            )
        
        # Validate expected columns exist
        if "item" not in raw_df.columns or "value" not in raw_df.columns:
            raise RuntimeError(
                f"Xueqiu API returned unexpected data structure. "
                f"Expected columns 'item' and 'value', got: {raw_df.columns.tolist()}"
            )

        # Convert to dictionary for easier lookup
        try:
            data_map = dict(zip(raw_df["item"], raw_df["value"], strict=True))
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse Xueqiu data structure: {e}"
            ) from e

        def _get_value(key: str, type_func: type = float) -> float | str:
            val = data_map.get(key)
            if val is None:
                return 0.0 if type_func in (float, int) else ""
            try:
                result = type_func(val)
                if isinstance(result, (float, int)):
                    return float(result)
                return str(result)
            except (ValueError, TypeError):
                return 0.0 if type_func in (float, int) else ""

        # Transform to match standard format
        try:
            data = {
                "symbol": self.symbol,
                "price": _get_value("现价"),
                "change": _get_value("涨跌"),
                "pct_change": _get_value("涨幅"),
                "timestamp": pd.to_datetime(_get_value("时间", str)).tz_localize("Asia/Shanghai"),
                "volume": float(_get_value("成交量", int)) / 100,
                "amount": _get_value("成交额"),
                "open": _get_value("今开"),
                "high": _get_value("最高"),
                "low": _get_value("最低"),
                "prev_close": _get_value("昨收"),
            }
        except Exception as e:
            raise RuntimeError(
                f"Failed to transform Xueqiu data to standard format: {e}"
            ) from e

        return pd.DataFrame([data])
