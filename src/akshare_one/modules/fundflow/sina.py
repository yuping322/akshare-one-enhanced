"""
Sina fund flow data provider.

This module implements the fund flow data provider using Sina as the data source.
"""

import pandas as pd

from .base import FundFlowProvider


class SinaFundFlowProvider(FundFlowProvider):
    """
    Fund flow data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sina"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get individual stock fund flow data from Sina."""
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        return self.create_empty_dataframe(
            [
                "date",
                "symbol",
                "name",
                "net_inflow",
                "net_inflow_rate",
                "main_inflow",
                "main_inflow_rate",
                "retail_inflow",
                "retail_inflow_rate",
            ]
        )

    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get sector fund flow data from Sina."""
        self.validate_date_range(start_date, end_date)
        if sector_type not in ["industry", "concept"]:
            raise ValueError("sector_type must be 'industry' or 'concept'")
        return self.create_empty_dataframe(
            ["date", "sector_code", "sector_name", "net_inflow", "net_inflow_rate", "up_count", "down_count"]
        )

    def get_main_fund_flow_rank(self, date: str, indicator: str) -> pd.DataFrame:
        """Get main fund flow ranking from Sina."""
        if indicator not in ["net_inflow", "net_inflow_rate"]:
            raise ValueError("indicator must be 'net_inflow' or 'net_inflow_rate'")
        return self.create_empty_dataframe(["rank", "symbol", "name", "net_inflow", "net_inflow_rate", "price"])

    def get_industry_list(self) -> pd.DataFrame:
        """Get list of industry sectors from Sina."""
        return self.create_empty_dataframe(["industry_code", "industry_name"])

    def get_industry_constituents(self, industry_code: str) -> pd.DataFrame:
        """Get constituent stocks of an industry sector from Sina."""
        return self.create_empty_dataframe(["symbol", "name", "weight", "net_inflow", "price_change"])

    def get_concept_list(self) -> pd.DataFrame:
        """Get list of concept sectors from Sina."""
        return self.create_empty_dataframe(["concept_code", "concept_name"])

    def get_concept_constituents(self, concept_code: str) -> pd.DataFrame:
        """Get constituent stocks of a concept sector from Sina."""
        return self.create_empty_dataframe(["symbol", "name", "weight", "net_inflow", "price_change"])
