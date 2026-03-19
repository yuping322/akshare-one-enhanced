"""
Base provider class for fund flow data.

This module defines the abstract interface for fund flow data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


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

    @abstractmethod
    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get individual stock fund flow data.
        """
        pass

    @abstractmethod
    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get sector fund flow data.
        """
        pass

    @abstractmethod
    def get_main_fund_flow_rank(self, date: str, indicator: str) -> pd.DataFrame:
        """
        Get main fund flow ranking.
        """
        pass

    @abstractmethod
    def get_industry_list(self) -> pd.DataFrame:
        """
        Get list of industry sectors.
        """
        pass

    @abstractmethod
    def get_industry_constituents(self, industry_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of an industry sector.
        """
        pass

    @abstractmethod
    def get_concept_list(self) -> pd.DataFrame:
        """
        Get list of concept sectors.
        """
        pass

    @abstractmethod
    def get_concept_constituents(self, concept_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of a concept sector.
        """
        pass


class FundFlowFactory(BaseFactory["FundFlowProvider"]):
    """
    Factory class for creating fund flow data providers.
    """

    _providers: dict[str, type["FundFlowProvider"]] = {}
