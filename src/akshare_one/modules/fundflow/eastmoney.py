"""
Eastmoney fund flow data provider.

This module implements the fund flow data provider using Eastmoney as the data source.
"""

import pandas as pd

from ...akshare_compat import call_akshare
from .base import FundFlowProvider, FundFlowFactory


@FundFlowFactory.register("eastmoney")
class EastmoneyFundFlowProvider(FundFlowProvider):
    _API_MAP = {
        "get_industry_list": {
            "ak_func": "stock_board_industry_name_em",
        },
        "get_industry_constituents": {
            "ak_func": "stock_board_industry_cons_em",
            "params": {"symbol": "industry_code"},
        },
        "get_concept_list": {
            "ak_func": "stock_board_concept_name_em",
        },
        "get_concept_constituents": {
            "ak_func": "stock_board_concept_cons_em",
            "params": {"symbol": "concept_code"},
        },
        "get_main_fund_flow_rank": {
            "ak_func": "stock_individual_fund_flow_rank",
            "params": {"indicator": "indicator_raw"},
        },
    }

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """Get individual stock fund flow data from Eastmoney."""
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        try:
            market = "sh" if symbol.startswith("6") else "sz"
            # Use adapter to call akshare (handles function drift)
            raw_df = call_akshare(
                "stock_individual_fund_flow",
                stock=symbol,
                market=market,
                fallback_func="stock_fund_flow_individual",  # Fallback for older versions
            )
        except Exception as e:
            self.logger.error(f"Failed to fetch stock fund flow for {symbol}: {e}")
            raise RuntimeError(f"Failed to fetch stock fund flow data: {str(e)}") from e

        df = self.standardize_and_filter(raw_df, source="eastmoney", **kwargs)
        if not df.empty:
            df["symbol"] = symbol
            if "date" in df.columns:
                df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df

    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """Get sector fund flow data from Eastmoney."""
        if sector_type not in ["industry", "concept"]:
            raise ValueError(f"Invalid sector_type: {sector_type}")

        try:
            ak_sector = "行业资金流" if sector_type == "industry" else "概念资金流"
            # Use adapter to call akshare (handles function drift)
            raw_df = call_akshare(
                "stock_sector_fund_flow_rank",
                indicator="今日",
                sector_type=ak_sector,
            )
        except Exception as e:
            self.logger.warning(f"Failed to fetch sector fund flow for {sector_type}: {e}")
            return pd.DataFrame()

        df = self.standardize_and_filter(raw_df, "eastmoney", **kwargs)
        if not df.empty:
            if "date" in df.columns:
                df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df

    def get_main_fund_flow_rank(self, date: str, indicator: str, **kwargs) -> pd.DataFrame:
        """Get main fund flow ranking from Eastmoney."""
        self.validate_date(date)

        # Validate indicator parameter
        if not indicator:
            raise ValueError("indicator cannot be empty")

        # Map English indicators to Chinese values expected by akshare API
        indicator_mapping = {
            "today": "今日",
            "3day": "3日",
            "5day": "5日",
            "10day": "10日",
            "main_net_inflow": "今日",  # Default mapping for common use
            "net_inflow": "今日",
            "net_inflow_rate": "今日",
        }

        # If indicator is already in Chinese format, use it directly
        valid_chinese_indicators = ["今日", "3日", "5日", "10日"]
        if indicator in valid_chinese_indicators:
            indicator_raw = indicator
        # Otherwise, map from English to Chinese
        elif indicator in indicator_mapping:
            indicator_raw = indicator_mapping[indicator]
        else:
            valid_english = list(indicator_mapping.keys())
            raise ValueError(
                f"Invalid indicator: {indicator}. Must be one of {valid_chinese_indicators} (Chinese) "
                f"or {valid_english} (English)"
            )

        kwargs["indicator_raw"] = indicator_raw
        try:
            return self._execute_api_mapped("get_main_fund_flow_rank", **kwargs)
        except Exception as e:
            self.logger.warning(f"Failed to fetch main fund flow rank: {e}")
            return pd.DataFrame()

    def get_industry_constituents(self, industry_code: str, **kwargs) -> pd.DataFrame:
        """Get constituent stocks of an industry sector."""
        # Validate industry_code parameter
        if not industry_code:
            raise ValueError("industry_code cannot be empty")

        return self._execute_api_mapped("get_industry_constituents", industry_code=industry_code, **kwargs)

    def get_concept_constituents(self, concept_code: str, **kwargs) -> pd.DataFrame:
        """Get constituent stocks of a concept sector."""
        # Validate concept_code parameter
        if not concept_code:
            raise ValueError("concept_code cannot be empty")

        return self._execute_api_mapped("get_concept_constituents", concept_code=concept_code, **kwargs)

    def get_sector_list(self, sector_type: str = "industry", **kwargs) -> pd.DataFrame:
        """
        Get list of sectors (industry or concept).

        Args:
            sector_type: 'industry' or 'concept'

        Returns:
            pd.DataFrame: Sector list
        """
        if sector_type == "industry":
            return self._execute_api_mapped("get_industry_list", **kwargs)
        elif sector_type == "concept":
            return self._execute_api_mapped("get_concept_list", **kwargs)
        else:
            raise ValueError(f"Invalid sector_type: {sector_type}. Must be 'industry' or 'concept'")

    def get_sector_constituents(self, sector_code: str, sector_type: str = "industry", **kwargs) -> pd.DataFrame:
        """
        Get constituent stocks of a sector.

        Args:
            sector_code: Sector code or name
            sector_type: 'industry' or 'concept'

        Returns:
            pd.DataFrame: Constituent stocks
        """
        if sector_type == "industry":
            return self.get_industry_constituents(industry_code=sector_code, **kwargs)
        elif sector_type == "concept":
            return self.get_concept_constituents(concept_code=sector_code, **kwargs)
        else:
            raise ValueError(f"Invalid sector_type: {sector_type}. Must be 'industry' or 'concept'")
