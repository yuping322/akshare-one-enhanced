"""
Lixinger provider for equity pledge data.

This module implements equity pledge data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import EquityPledgeFactory, EquityPledgeProvider


@EquityPledgeFactory.register("lixinger")
class LixingerPledgeProvider(EquityPledgeProvider):
    """
    Equity pledge data provider using Lixinger OpenAPI.

    Provides equity pledge details including pledgor, pledgee, and pledge amounts.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_equity_pledge(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get equity pledge data from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000'). Required for Lixinger API.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Equity pledge data with columns:
                - symbol: Stock symbol
                - date: Data date (YYYY-MM-DD)
                - pledgor: Pledgor name (出质人)
                - pledgee: Pledgee name (质权人)
                - pledge_matters: Pledge matters (质押事项)
                - pledge_shares_nature: Pledge shares nature (质押股份性质)
                - pledge_amount: Pledge amount (质押数量)
                - pledge_ratio: Pledge ratio of total equity (占总股比例)
                - pledge_start_date: Pledge start date (质押起始日)
                - pledge_end_date: Pledge end date (质押终止日)
                - pledge_discharge_date: Pledge discharge date (质押解除日)
                - pledge_discharge_explanation: Pledge discharge explanation (质押解除解释)
                - pledge_discharge_amount: Pledge discharge amount (质押解除数量)
                - is_pledge_repurchase: Is pledge repurchase transaction (是否质押式回购交易)
                - accumulated_pledge_ratio: Accumulated pledge ratio of total equity (累计质押占总股比例)

        Raises:
            ValueError: If symbol is not provided
            RuntimeError: If API request fails
        """
        if not symbol:
            raise ValueError("symbol is required for Lixinger equity pledge API")

        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        client = get_lixinger_client()

        params = {
            "stockCode": symbol,
            "startDate": start_date,
            "endDate": end_date,
        }

        if kwargs.get("limit"):
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/pledge", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        standardized = pd.DataFrame()

        standardized["symbol"] = symbol.zfill(6)

        if "date" in df.columns:
            standardized["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        else:
            standardized["date"] = ""

        if "pledgor" in df.columns:
            standardized["pledgor"] = df["pledgor"].astype(str)
        else:
            standardized["pledgor"] = ""

        if "pledgee" in df.columns:
            standardized["pledgee"] = df["pledgee"].astype(str)
        else:
            standardized["pledgee"] = ""

        if "pledgeMatters" in df.columns:
            standardized["pledge_matters"] = df["pledgeMatters"].astype(str)
        else:
            standardized["pledge_matters"] = ""

        if "pledgeSharesNature" in df.columns:
            standardized["pledge_shares_nature"] = df["pledgeSharesNature"].astype(str)
        else:
            standardized["pledge_shares_nature"] = ""

        if "pledgeAmount" in df.columns:
            standardized["pledge_amount"] = pd.to_numeric(df["pledgeAmount"], errors="coerce").fillna(0.0)
        else:
            standardized["pledge_amount"] = 0.0

        if "pledgePercentageOfTotalEquity" in df.columns:
            standardized["pledge_ratio"] = pd.to_numeric(df["pledgePercentageOfTotalEquity"], errors="coerce").fillna(
                0.0
            )
        else:
            standardized["pledge_ratio"] = 0.0

        if "pledgeStartDate" in df.columns:
            standardized["pledge_start_date"] = pd.to_datetime(df["pledgeStartDate"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )
            standardized["pledge_start_date"] = standardized["pledge_start_date"].fillna("")
        else:
            standardized["pledge_start_date"] = ""

        if "pledgeEndDate" in df.columns:
            standardized["pledge_end_date"] = pd.to_datetime(df["pledgeEndDate"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )
            standardized["pledge_end_date"] = standardized["pledge_end_date"].fillna("")
        else:
            standardized["pledge_end_date"] = ""

        if "pledgeDischargeDate" in df.columns:
            standardized["pledge_discharge_date"] = pd.to_datetime(
                df["pledgeDischargeDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            standardized["pledge_discharge_date"] = standardized["pledge_discharge_date"].fillna("")
        else:
            standardized["pledge_discharge_date"] = ""

        if "pledgeDischargeExplanation" in df.columns:
            standardized["pledge_discharge_explanation"] = df["pledgeDischargeExplanation"].astype(str)
        else:
            standardized["pledge_discharge_explanation"] = ""

        if "pledgeDischargeAmount" in df.columns:
            standardized["pledge_discharge_amount"] = pd.to_numeric(
                df["pledgeDischargeAmount"], errors="coerce"
            ).fillna(0.0)
        else:
            standardized["pledge_discharge_amount"] = 0.0

        if "isPledgeRepurchaseTransactions" in df.columns:
            standardized["is_pledge_repurchase"] = df["isPledgeRepurchaseTransactions"].astype(bool)
        else:
            standardized["is_pledge_repurchase"] = False

        if "accumulatedPledgePercentageOfTotalEquity" in df.columns:
            standardized["accumulated_pledge_ratio"] = pd.to_numeric(
                df["accumulatedPledgePercentageOfTotalEquity"], errors="coerce"
            ).fillna(0.0)
        else:
            standardized["accumulated_pledge_ratio"] = 0.0

        return self.standardize_and_filter(
            standardized, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_equity_pledge_ratio_rank(self, date: str, top_n: int, **kwargs) -> pd.DataFrame:
        """
        Get equity pledge ratio ranking.

        Note: Lixinger doesn't provide this functionality.
        This method returns empty DataFrame.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()
