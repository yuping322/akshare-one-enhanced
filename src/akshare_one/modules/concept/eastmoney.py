"""
Eastmoney concept sector data provider.
"""

import pandas as pd

from .base import ConceptProvider, ConceptFactory


@ConceptFactory.register("eastmoney")
class EastmoneyConceptProvider(ConceptProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_concept_list()

    def get_concept_list(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get concept sector list from Eastmoney.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Concept sectors with quotes.
        """
        import akshare as ak

        try:
            df = ak.stock_board_concept_name_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch concept list: {e}")
            return pd.DataFrame()

    def get_concept_stocks(
        self,
        concept: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get stocks in a specific concept sector.

        Args:
            concept: Concept sector name or code.
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Stocks with quotes.
        """
        import akshare as ak

        try:
            df = ak.stock_board_concept_cons_em(symbol=concept)
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch concept stocks for {concept}: {e}")
            return pd.DataFrame()
