"""
Base provider class for fund flow data.

This module defines the abstract interface for fund flow data providers.
"""

from typing import Any

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class FundFlowProvider(BaseProvider):
    """
    Abstract base class for fund flow data providers.

    Defines the interface for fetching various types of fund flow data.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "fundflow"

    def get_update_frequency(self) -> str:
        """Fund flow data is updated in realtime."""
        return "realtime"

    def get_delay_minutes(self) -> int:
        """Fund flow data has minimal delay."""
        return 0

    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get individual stock fund flow data.
        """
        return self._execute_api_mapped(
            "get_stock_fund_flow", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get sector fund flow data.
        """
        return self._execute_api_mapped(
            "get_sector_fund_flow", sector_type=sector_type, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_main_fund_flow_rank(self, date: str, indicator: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get main fund flow ranking.
        """
        return self._execute_api_mapped("get_main_fund_flow_rank", date=date, indicator=indicator, **kwargs)

    def get_industry_list(self, **kwargs: Any) -> pd.DataFrame:
        """
        Get list of industry sectors.
        """
        return self._execute_api_mapped("get_industry_list", **kwargs)

    def get_industry_constituents(self, industry_code: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get constituent stocks of an industry sector.
        """
        return self._execute_api_mapped("get_industry_constituents", industry_code=industry_code, **kwargs)

    def get_concept_list(self, **kwargs: Any) -> pd.DataFrame:
        """
        Get list of concept sectors.
        """
        return self._execute_api_mapped("get_concept_list", **kwargs)

    def get_concept_constituents(self, concept_code: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get constituent stocks of a concept sector.
        """
        return self._execute_api_mapped("get_concept_constituents", concept_code=concept_code, **kwargs)

    def get_sector_list(self, sector_type: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get list of sectors (industry or concept).
        """
        return self._execute_api_mapped("get_sector_list", sector_type=sector_type, **kwargs)

    def get_sector_constituents(self, sector_code: str, **kwargs: Any) -> pd.DataFrame:
        """
        Get constituent stocks of a sector.
        """
        return self._execute_api_mapped("get_sector_constituents", sector_code=sector_code, **kwargs)


class FundFlowFactory(BaseFactory["FundFlowProvider"]):
    """
    Factory class for creating fund flow data providers.
    """

    _providers: dict[str, type["FundFlowProvider"]] = {}
