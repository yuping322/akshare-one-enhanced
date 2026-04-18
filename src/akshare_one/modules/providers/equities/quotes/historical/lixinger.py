"""
Lixinger provider for historical data (K-line).

This module implements historical/K-line data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ......lixinger_client import get_lixinger_client
from .base import HistoricalDataFactory, HistoricalDataProvider


@HistoricalDataFactory.register("lixinger")
class LixingerHistoricalProvider(HistoricalDataProvider):
    """
    Historical/K-line data provider using Lixinger OpenAPI.

    Provides candlestick data with different adjustment types.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get historical/K-line data from Lixinger.

        Args:
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Candlestick data with columns:
                - date: Date
                - open: Open price
                - close: Close price
                - high: High price
                - low: Low price
                - volume: Volume
                - amount: Amount
                - change_pct: Change percentage
                - turnover_rate: Turnover rate
        """
        client = get_lixinger_client()

        adjust_type_map = {"none": "ex_rights", "qfq": "lxr_fc_rights", "hfq": "bc_rights"}

        adjust_type = adjust_type_map.get(self.adjust, "lxr_fc_rights")

        params = {"stockCode": self.symbol, "type": adjust_type, "startDate": self.start_date, "endDate": self.end_date}

        if self.interval != "day":
            self.logger.warning(
                f"Lixinger only supports daily data. Requested interval '{self.interval}' will be ignored.",
                extra={
                    "context": {
                        "log_type": "unsupported_interval",
                        "provider": "lixinger",
                        "requested_interval": self.interval,
                    }
                },
            )

        response = client.query_api("cn/company/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)
