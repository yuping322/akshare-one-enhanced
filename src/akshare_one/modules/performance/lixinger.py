"""
Lixinger provider for performance data.

Uses cn/company/fs/non_financial to derive performance express data
(revenue, net profit, EPS, ROE) as a backup to the eastmoney source.

Note: Lixinger does not provide a performance-forecast (业绩预告) endpoint,
so get_performance_forecast returns an empty DataFrame.
"""

import time

import pandas as pd

from ...lixinger_client import get_lixinger_client
from ....metrics.stats import get_stats_collector
from ...constants import SYMBOL_ZFILL_WIDTH
from .base import PerformanceFactory, PerformanceProvider


@PerformanceFactory.register("lixinger")
class LixingerPerformanceProvider(PerformanceProvider):
    """
    Performance data provider using Lixinger OpenAPI.

    get_performance_express  → cn/company/fs/non_financial
    get_performance_forecast → not supported (returns empty DataFrame)
    """

    # Key financial metrics for a performance express
    _EXPRESS_METRICS = [
        "q.ps.toi.t",  # revenue (营业总收入)
        "q.ps.ni.t",  # net income (净利润)
        "q.ps.op.t",  # operating profit (营业利润)
        "q.bs.te.t",  # shareholders equity (净资产)
        "q.i.eps.t",  # EPS (每股收益)
        "q.i.roe.t",  # ROE (净资产收益率)
    ]

    _COLUMN_MAP = {
        "date": "report_date",
        "stockCode": "symbol",
        "q.ps.toi.t": "revenue",
        "q.ps.ni.t": "net_profit",
        "q.ps.op.t": "operating_profit",
        "q.bs.te.t": "net_assets",
        "q.i.eps.t": "eps",
        "q.i.roe.t": "roe",
    }

    def get_source_name(self) -> str:
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_performance_express(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Get performance express data from Lixinger financial statements.

        Args:
            date: Report period end date, e.g. '20231231' or '2023-12-31'.
                  Lixinger accepts YYYY-MM-DD format.

        Returns:
            pd.DataFrame with columns:
                symbol, name, report_date, revenue, net_profit,
                operating_profit, net_assets, eps, roe
        """
        start_time = time.time()
        try:
            norm_date = date.replace("-", "")
            lx_date = f"{norm_date[:4]}-{norm_date[4:6]}-{norm_date[6:]}"

            client = get_lixinger_client()
            params = {
                "metricsList": self._EXPRESS_METRICS,
                "date": lx_date,
            }

            response = client.query_api("cn/company/fs/non_financial", params)

            if response.get("code") != 1:
                self.logger.warning(f"Lixinger fs/non_financial returned error: {response.get('msg')}")
                return self.create_empty_dataframe(
                    ["symbol", "report_date", "revenue", "net_profit", "operating_profit", "net_assets", "eps", "roe"]
                )

            data = response.get("data", [])
            if not data:
                return self.create_empty_dataframe(
                    ["symbol", "report_date", "revenue", "net_profit", "operating_profit", "net_assets", "eps", "roe"]
                )

            df = pd.json_normalize(data)
            df = df.rename(columns=self._COLUMN_MAP)

            if "symbol" in df.columns:
                df["symbol"] = df["symbol"].astype(str).str.zfill(SYMBOL_ZFILL_WIDTH)
            if "report_date" in df.columns:
                df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce").dt.strftime("%Y-%m-%d")

            numeric_cols = ["revenue", "net_profit", "operating_profit", "net_assets", "eps", "roe"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            columns = kwargs.get("columns")
            row_filter = kwargs.get("row_filter")
            result = self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

    def get_performance_forecast(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Lixinger does not provide performance forecast (业绩预告) data.
        Returns empty DataFrame.
        """
        self.logger.warning(
            "Lixinger does not support performance forecast (get_performance_forecast). "
            "Use eastmoney source for this query."
        )
        return self.create_empty_dataframe(
            ["symbol", "name", "indicator", "change", "forecast_value", "change_pct", "forecast_type", "announce_date"]
        )
