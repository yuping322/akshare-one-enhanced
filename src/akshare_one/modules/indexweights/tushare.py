from ..base import BaseProvider
import pandas as pd


class TushareIndexWeightsProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "tushare"

    def get_index_weights(self, index_code: str, date: str = "") -> pd.DataFrame:
        from ...tushare_client import get_tushare_client

        client = get_tushare_client()
        if date:
            return client.get_index_weight(index_code=index_code, trade_date=date)
        return client.get_index_weight(index_code=index_code)

    def get_index_weights_history(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        from ...tushare_client import get_tushare_client

        client = get_tushare_client()
        return client.get_index_weight(index_code=index_code, start_date=start_date, end_date=end_date)

    def get_index_info(self, index_code: str = "") -> pd.DataFrame:
        from ...tushare_client import get_tushare_client

        client = get_tushare_client()
        df = client.get_index_basic()
        if index_code and not df.empty:
            for col in ["ts_code", "index_code"]:
                if col in df.columns:
                    df = df[df[col] == index_code]
                    break
        return df


from .base import IndexWeightsFactory

IndexWeightsFactory._providers["tushare"] = TushareIndexWeightsProvider
