"""
Official macro economic data provider.

This module implements the macro data provider using official sources
(央行, 统计局) via akshare.
"""

import pandas as pd

from .base import MacroProvider


class OfficialMacroProvider(MacroProvider):
    """
    Macro economic data provider using official sources.
    
    This provider wraps akshare functions to fetch macro data from official
    sources and standardizes the output format for consistency.
    """
    
    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'official'
    
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from official sources.
        
        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.
        
        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()
    
    def get_lpr_rate(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) interest rate data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized LPR rate data with columns:
                - date: Date (YYYY-MM-DD)
                - lpr_1y: 1-year LPR rate (%)
                - lpr_5y: 5-year LPR rate (%)
        
        Example:
            >>> provider = OfficialMacroProvider()
            >>> df = provider.get_lpr_rate('2024-01-01', '2024-12-31')
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_lpr()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'lpr_1y', 'lpr_5y'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['TRADE_DATE']).dt.strftime('%Y-%m-%d')
            standardized['lpr_1y'] = raw_df['LPR1Y'].astype(float)
            standardized['lpr_5y'] = raw_df['LPR5Y'].astype(float)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch LPR rate data: {e}") from e
    
    def get_pmi_index(
        self,
        start_date: str,
        end_date: str,
        pmi_type: str
    ) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            pmi_type: PMI type ('manufacturing', 'non_manufacturing', or 'caixin')
        
        Returns:
            pd.DataFrame: Standardized PMI index data with columns:
                - date: Date (YYYY-MM-DD)
                - pmi_value: PMI value
                - yoy: Year-over-year change
                - mom: Month-over-month change
        
        Raises:
            ValueError: If pmi_type is invalid
        """
        self.validate_date_range(start_date, end_date)
        
        if pmi_type not in ['manufacturing', 'non_manufacturing', 'caixin']:
            raise ValueError(
                f"Invalid pmi_type: {pmi_type}. "
                "Must be 'manufacturing', 'non_manufacturing', or 'caixin'"
            )
        
        try:
            import akshare as ak
            
            # Call appropriate akshare function based on PMI type
            if pmi_type == 'manufacturing':
                raw_df = ak.macro_china_pmi()
            elif pmi_type == 'non_manufacturing':
                raw_df = ak.macro_china_non_man_pmi()
            else:  # caixin
                raw_df = ak.macro_china_cx_pmi()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'pmi_value', 'yoy', 'mom'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            
            # Parse Chinese date format (e.g., "2026年01月份" -> "2026-01-01")
            def parse_chinese_date(date_str):
                """Parse Chinese date format like '2026年01月份' to 'YYYY-MM-DD'"""
                import re
                match = re.match(r'(\d{4})年(\d{2})月份?', str(date_str))
                if match:
                    year, month = match.groups()
                    return f"{year}-{month}-01"
                return date_str
            
            standardized['date'] = raw_df['月份'].apply(parse_chinese_date)
            
            # Select the appropriate column based on PMI type
            if pmi_type == 'manufacturing':
                standardized['pmi_value'] = raw_df['制造业-指数'].astype(float)
                standardized['yoy'] = raw_df.get('制造业-同比增长', None)
            elif pmi_type == 'non_manufacturing':
                standardized['pmi_value'] = raw_df['非制造业-指数'].astype(float)
                standardized['yoy'] = raw_df.get('非制造业-同比增长', None)
            else:  # caixin
                standardized['pmi_value'] = raw_df['指数'].astype(float)
                standardized['yoy'] = None
            
            # MoM is typically not provided in raw data, set to None
            standardized['mom'] = None
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch PMI index data: {e}") from e
    
    def get_cpi_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized CPI data with columns:
                - date: Date (YYYY-MM-DD)
                - current: Current month value
                - yoy: Year-over-year change (%)
                - mom: Month-over-month change (%)
                - cumulative: Cumulative value
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_cpi()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'current', 'yoy', 'mom', 'cumulative'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['月份']).dt.strftime('%Y-%m-%d')
            standardized['current'] = raw_df.get('当月', 0.0).astype(float)
            standardized['yoy'] = raw_df.get('同比增长', 0.0).astype(float)
            standardized['mom'] = raw_df.get('环比增长', 0.0).astype(float)
            standardized['cumulative'] = raw_df.get('累计', 0.0).astype(float)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch CPI data: {e}") from e
    
    def get_ppi_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized PPI data with columns:
                - date: Date (YYYY-MM-DD)
                - current: Current month value
                - yoy: Year-over-year change (%)
                - mom: Month-over-month change (%)
                - cumulative: Cumulative value
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_ppi()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'current', 'yoy', 'mom', 'cumulative'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['月份']).dt.strftime('%Y-%m-%d')
            standardized['current'] = raw_df.get('当月', 0.0).astype(float)
            standardized['yoy'] = raw_df.get('同比增长', 0.0).astype(float)
            standardized['mom'] = raw_df.get('环比增长', 0.0).astype(float)
            standardized['cumulative'] = raw_df.get('累计', 0.0).astype(float)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch PPI data: {e}") from e
    
    def get_m2_supply(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get M2 money supply data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized M2 supply data with columns:
                - date: Date (YYYY-MM-DD)
                - m2_balance: M2 balance (billion yuan) - Not available, set to None
                - yoy_growth_rate: Year-over-year growth rate (%)
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_m2_yearly()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'm2_balance', 'yoy_growth_rate'
                ])
            
            # Standardize the data
            # Note: The akshare API returns columns: '商品', '日期', '今值', '预测值', '前值'
            # '今值' is the current year-over-year growth rate
            # M2 balance data is not available from this API
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['日期']).dt.strftime('%Y-%m-%d')
            standardized['m2_balance'] = None  # Not available from this API
            standardized['yoy_growth_rate'] = pd.to_numeric(raw_df['今值'], errors='coerce')
            
            # Filter out rows with None/NaN yoy_growth_rate
            standardized = standardized.dropna(subset=['yoy_growth_rate']).reset_index(drop=True)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch M2 supply data: {e}") from e
    
    def get_shibor_rate(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) interest rate data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized Shibor rate data with columns:
                - date: Date (YYYY-MM-DD)
                - overnight: Overnight rate (%)
                - week_1: 1-week rate (%)
                - week_2: 2-week rate (%)
                - month_1: 1-month rate (%)
                - month_3: 3-month rate (%)
                - month_6: 6-month rate (%)
                - month_9: 9-month rate (%)
                - year_1: 1-year rate (%)
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_shibor_all()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'overnight', 'week_1', 'week_2', 'month_1',
                    'month_3', 'month_6', 'month_9', 'year_1'
                ])
            
            # Standardize the data
            # Note: akshare column names changed from '隔夜', '1周' to 'O/N-定价', '1W-定价'
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['日期']).dt.strftime('%Y-%m-%d')
            
            # Try new format first, fall back to old format
            if 'O/N-定价' in raw_df.columns:
                # New format (as of 2025)
                standardized['overnight'] = raw_df['O/N-定价'].astype(float)
                standardized['week_1'] = raw_df['1W-定价'].astype(float)
                standardized['week_2'] = raw_df['2W-定价'].astype(float)
                standardized['month_1'] = raw_df['1M-定价'].astype(float)
                standardized['month_3'] = raw_df['3M-定价'].astype(float)
                standardized['month_6'] = raw_df['6M-定价'].astype(float)
                standardized['month_9'] = raw_df['9M-定价'].astype(float)
                standardized['year_1'] = raw_df['1Y-定价'].astype(float)
            else:
                # Old format (before 2025)
                standardized['overnight'] = raw_df['隔夜'].astype(float)
                standardized['week_1'] = raw_df['1周'].astype(float)
                standardized['week_2'] = raw_df['2周'].astype(float)
                standardized['month_1'] = raw_df['1月'].astype(float)
                standardized['month_3'] = raw_df['3月'].astype(float)
                standardized['month_6'] = raw_df['6月'].astype(float)
                standardized['month_9'] = raw_df['9月'].astype(float)
                standardized['year_1'] = raw_df['1年'].astype(float)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Shibor rate data: {e}") from e
    
    def get_social_financing(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get social financing scale data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized social financing data with columns:
                - date: Date (YYYY-MM-DD)
                - total_scale: Total social financing scale (billion yuan)
                - yoy: Year-over-year change (%)
                - mom: Month-over-month change (%)
                - new_rmb_loans: New RMB loans (billion yuan)
        """
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.macro_china_shrzgm()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'total_scale', 'yoy', 'mom', 'new_rmb_loans'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['月份']).dt.strftime('%Y-%m-%d')
            standardized['total_scale'] = raw_df['社会融资规模增量(亿元)'].astype(float)
            # YoY and MoM are typically not provided in raw data, set to None
            standardized['yoy'] = None
            standardized['mom'] = None
            standardized['new_rmb_loans'] = raw_df.get('新增人民币贷款(亿元)', 0.0).astype(float)
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch social financing data: {e}") from e
