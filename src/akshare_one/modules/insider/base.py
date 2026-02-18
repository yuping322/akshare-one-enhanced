from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class InsiderDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "insider"

    def get_data_type(self) -> str:
        return "insider"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_inner_trade_data()

    @abstractmethod
    def get_inner_trade_data(self) -> pd.DataFrame:
        """Fetches insider trade data

        Returns:
            pd.DataFrame:
            - symbol: 股票代码
            - issuer: 股票名称
            - name: 变动人
            - title: 董监高职务
            - transaction_date: 变动日期
            - transaction_shares: 变动股数
            - transaction_price_per_share: 成交均价
            - shares_owned_after_transaction: 变动后持股数
            - relationship: 与董监高关系
            - is_board_director: 是否为董事会成员
            - transaction_value: 交易金额(变动股数*成交均价)
            - shares_owned_before_transaction: 变动前持股数
        """
        pass
