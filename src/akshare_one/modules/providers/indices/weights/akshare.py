"""
AkShare provider for index weights data.
"""

import pandas as pd

from .base import IndexWeightsFactory, IndexWeightsProvider


@IndexWeightsFactory.register("akshare")
class AkShareIndexWeightsProvider(IndexWeightsProvider):
    """Index weights data provider using AkShare."""

    def get_source_name(self) -> str:
        return "akshare"

    def get_index_weights(self, index_code: str, date: str = "") -> pd.DataFrame:
        """Get index weights using CSIndex API."""
        if date:
            df = self.akshare_adapter.call(
                "index_stock_cons_weight_csindex", index_code=index_code, start_date=date, end_date=date
            )
        else:
            df = self.akshare_adapter.call("index_stock_cons_weight_csindex", index_code=index_code)
        return df

    def get_index_weights_history(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get index weights history."""
        df = self.akshare_adapter.call(
            "index_stock_cons_weight_csindex", index_code=index_code, start_date=start_date, end_date=end_date
        )
        return df

    def get_index_info(self, index_code: str = "") -> pd.DataFrame:
        """Get index information."""
        df = self.akshare_adapter.call("index_stock_info")
        if index_code and not df.empty:
            for col in ["指数代码", "index_code", "code"]:
                if col in df.columns:
                    df = df[df[col] == index_code]
                    break
        return df
