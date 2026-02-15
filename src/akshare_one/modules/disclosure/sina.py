"""
Sina disclosure news data provider.

This module implements the disclosure news data provider using Sina as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from .base import DisclosureProvider


class SinaDisclosureProvider(DisclosureProvider):
    """
    Disclosure news data provider using Sina as the data source.

    This provider wraps akshare functions to fetch disclosure news data from Sina
    and standardizes the output format for consistency.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'sina'

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Sina.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_disclosure_news(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        category: str
    ) -> pd.DataFrame:
        """
        Get disclosure news data from Sina.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')

        Returns:
            pd.DataFrame: Standardized disclosure news data with columns:
                - date: Announcement date (YYYY-MM-DD)
                - symbol: Stock symbol
                - title: Announcement title
                - category: Announcement category
                - content: Announcement summary
                - url: Announcement URL

        Raises:
            ValueError: If parameters are invalid
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        if category not in ['all', 'dividend', 'repurchase', 'st', 'major_event']:
            raise ValueError(
                f"Invalid category: {category}. "
                "Must be one of: 'all', 'dividend', 'repurchase', 'st', 'major_event'"
            )

        try:
            import akshare as ak
            from datetime import datetime, timedelta

            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')

            all_data = []
            current_dt = start_dt

            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y%m%d')
                try:
                    df = ak.stock_notice_report(symbol="全部", date=date_str)
                    if not df.empty:
                        all_data.append(df)
                except Exception:
                    pass

                current_dt += timedelta(days=1)

            if not all_data:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'title', 'category', 'content', 'url'
                ])

            raw_df = pd.concat(all_data, ignore_index=True)
            return self._standardize_disclosure_news(raw_df, symbol, category)

        except Exception:
            return self.create_empty_dataframe([
                'date', 'symbol', 'title', 'category', 'content', 'url'
            ])

    def _standardize_disclosure_news(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None,
        category_filter: str
    ) -> pd.DataFrame:
        """Standardize disclosure news data."""
        if raw_df.empty:
            return self.create_empty_dataframe([
                'date', 'symbol', 'title', 'category', 'content', 'url'
            ])

        standardized = pd.DataFrame()
        standardized['date'] = pd.to_datetime(raw_df['公告日期']).dt.strftime('%Y-%m-%d')
        standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
        standardized['title'] = raw_df['公告标题'].astype(str)
        standardized['category'] = raw_df['公告类型'].astype(str)
        standardized['content'] = ''
        standardized['url'] = raw_df['公告链接'].astype(str) if '公告链接' in raw_df.columns else ''

        if symbol_filter:
            standardized = standardized[standardized['symbol'] == symbol_filter]

        if category_filter and category_filter != 'all':
            standardized = standardized[
                standardized['category'].str.contains(category_filter, case=False, na=False)
            ]

        return self.ensure_json_compatible(standardized.reset_index(drop=True))

    def get_dividend_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get dividend data from Sina.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized dividend data
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        # Return empty DataFrame with proper structure - Sina does not provide this data directly
        return self.create_empty_dataframe([
            'symbol', 'name', 'announcement_date', 'dividend_per_share',
            'bonus_shares', 'rights_issue_ratio', 'dividend_yield', 'record_date',
            'ex_date', 'payment_date'
        ])

    def _standardize_dividend_data(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None
    ) -> pd.DataFrame:
        """Standardize dividend data."""
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'name', 'announcement_date', 'dividend_per_share',
                'bonus_shares', 'rights_issue_ratio', 'dividend_yield', 'record_date',
                'ex_date', 'payment_date'
            ])

        standardized = pd.DataFrame()

        # Map common columns
        col_mapping = {
            '代码': 'symbol',
            '股票简称': 'name',
            '公告日期': 'announcement_date',
            '分红送转': 'dividend_per_share',
            '送转股': 'bonus_shares',
            '配股': 'rights_issue_ratio',
            '分红': 'dividend_per_share',
        }

        for cn_col, en_col in col_mapping.items():
            if cn_col in raw_df.columns:
                standardized[en_col] = raw_df[cn_col]

        if 'symbol' not in standardized.columns and '代码' in raw_df.columns:
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)

        if 'name' not in standardized.columns and '股票简称' in raw_df.columns:
            standardized['name'] = raw_df['股票简称']

        if symbol_filter:
            standardized = standardized[standardized['symbol'] == symbol_filter]

        return self.ensure_json_compatible(standardized.reset_index(drop=True))

    def get_repurchase_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get stock repurchase data from Sina.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized repurchase data
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        # Return empty DataFrame with proper structure - Sina does not provide this data directly
        return self.create_empty_dataframe([
            'symbol', 'name', 'announcement_date', 'repurchase_amount',
            'repurchase_ratio', 'average_price', 'progress', 'start_date',
            'end_date'
        ])

    def _standardize_repurchase_data(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None
    ) -> pd.DataFrame:
        """Standardize repurchase data."""
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'name', 'announcement_date', 'repurchase_amount',
                'repurchase_ratio', 'average_price', 'progress', 'start_date',
                'end_date'
            ])

        standardized = pd.DataFrame()

        col_mapping = {
            '代码': 'symbol',
            '股票简称': 'name',
            '公告日期': 'announcement_date',
            '回购金额': 'repurchase_amount',
            '回购比例': 'repurchase_ratio',
            '平均价格': 'average_price',
            '进度': 'progress',
            '起始日期': 'start_date',
            '截止日期': 'end_date',
        }

        for cn_col, en_col in col_mapping.items():
            if cn_col in raw_df.columns:
                standardized[en_col] = raw_df[cn_col]

        if 'symbol' not in standardized.columns and '代码' in raw_df.columns:
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)

        if symbol_filter:
            standardized = standardized[standardized['symbol'] == symbol_filter]

        return self.ensure_json_compatible(standardized.reset_index(drop=True))

    def get_st_delist_data(self, symbol: str | None) -> pd.DataFrame:
        """
        Get ST/delist risk data from Sina.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks

        Returns:
            pd.DataFrame: Standardized ST/delist risk data
        """
        if symbol:
            self.validate_symbol(symbol)

        # Return empty DataFrame with proper structure - Sina does not provide this data directly
        return self.create_empty_dataframe([
            'symbol', 'name', 'st_type', 'risk_level', 'reason',
            'announcement_date', 'delist_date'
        ])

    def _standardize_st_delist_data(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None
    ) -> pd.DataFrame:
        """Standardize ST/delist risk data."""
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'name', 'st_type', 'risk_level', 'reason',
                'announcement_date', 'delist_date'
            ])

        standardized = pd.DataFrame()

        col_mapping = {
            '代码': 'symbol',
            '名称': 'name',
            '类型': 'st_type',
            '风险等级': 'risk_level',
            '原因': 'reason',
            '公告日期': 'announcement_date',
            '退市日期': 'delist_date',
        }

        for cn_col, en_col in col_mapping.items():
            if cn_col in raw_df.columns:
                standardized[en_col] = raw_df[cn_col]

        if 'symbol' not in standardized.columns and '代码' in raw_df.columns:
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)

        if symbol_filter:
            standardized = standardized[standardized['symbol'] == symbol_filter]

        return self.ensure_json_compatible(standardized.reset_index(drop=True))
