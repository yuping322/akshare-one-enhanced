from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class RealtimeDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "realtime"

    def get_data_type(self) -> str:
        return "realtime"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_current_data()

    @abstractmethod
    def get_current_data(self) -> pd.DataFrame:
        """Fetches realtime market data

        Returns:
            pd.DataFrame:
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
        """
        pass
