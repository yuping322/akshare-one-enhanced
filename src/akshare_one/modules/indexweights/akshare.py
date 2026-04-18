from ..base import BaseProvider
import pandas as pd


class AkShareIndexWeightsProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "akshare"

    def get_index_weights(self, index_code: str, date: str = "") -> pd.DataFrame:
        """获取指数权重 - 使用中证指数公司API"""
        # ak.index_stock_cons_weight_csindex 获取权重
        if date:
            df = self.akshare_adapter.call(
                "index_stock_cons_weight_csindex", index_code=index_code, start_date=date, end_date=date
            )
        else:
            df = self.akshare_adapter.call("index_stock_cons_weight_csindex", index_code=index_code)
        return df

    def get_index_weights_history(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数权重历史"""
        df = self.akshare_adapter.call(
            "index_stock_cons_weight_csindex", index_code=index_code, start_date=start_date, end_date=end_date
        )
        return df

    def get_index_info(self, index_code: str = "") -> pd.DataFrame:
        """获取指数信息"""
        df = self.akshare_adapter.call("index_stock_info")
        if index_code and not df.empty:
            # Filter by index_code
            for col in ["指数代码", "index_code", "code"]:
                if col in df.columns:
                    df = df[df[col] == index_code]
                    break
        return df


from .base import IndexWeightsFactory

IndexWeightsFactory._providers["akshare"] = AkShareIndexWeightsProvider
