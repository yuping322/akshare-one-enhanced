"""
Base provider class for fund flow data.

This module defines the abstract interface for fund flow data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class FundFlowProvider(BaseProvider):
    """
    Abstract base class for fund flow data providers.

    Defines the interface for fetching various types of fund flow data:
    - Individual stock fund flow
    - Sector fund flow (industry and concept)
    - Main fund flow rankings
    - Sector lists and constituents
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

        Args:
            symbol: Stock symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized fund flow data
        """
        pass

    @abstractmethod
    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get sector fund flow data.

        Args:
            sector_type: Sector type ('industry' or 'concept')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized sector fund flow data
        """
        pass

    @abstractmethod
    def get_main_fund_flow_rank(self, date: str, indicator: str) -> pd.DataFrame:
        """
        Get main fund flow ranking.

        Args:
            date: Date (YYYY-MM-DD)
            indicator: Ranking indicator ('net_inflow' or 'net_inflow_rate')

        Returns:
            pd.DataFrame: Ranked fund flow data
        """
        pass

    @abstractmethod
    def get_industry_list(self) -> pd.DataFrame:
        """
        Get list of industry sectors.

        Returns:
            pd.DataFrame: Industry sector list with codes and names
        """
        pass

    @abstractmethod
    def get_industry_constituents(self, industry_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of an industry sector.

        Args:
            industry_code: Industry sector code

        Returns:
            pd.DataFrame: Constituent stocks with symbols and weights
        """
        pass

    @abstractmethod
    def get_concept_list(self) -> pd.DataFrame:
        """
        Get list of concept sectors.

        Returns:
            pd.DataFrame: Concept sector list with codes and names
        """
        pass

    @abstractmethod
    def get_concept_constituents(self, concept_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of a concept sector.

        Args:
            concept_code: Concept sector code

        Returns:
            pd.DataFrame: Constituent stocks with symbols and weights
        """
        pass
