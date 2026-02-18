"""
Eastmoney equity pledge data provider.

This module implements the equity pledge data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""


import pandas as pd

from .base import EquityPledgeProvider


class EastmoneyEquityPledgeProvider(EquityPledgeProvider):
    """
    Equity pledge data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch equity pledge data from Eastmoney
    and standardizes the output format for consistency.
    """
    
    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'eastmoney'
    
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Eastmoney.
        
        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.
        
        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()
    
    def get_equity_pledge(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get equity pledge data from Eastmoney.
        
        This method wraps akshare equity pledge functions and standardizes
        the output format.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized equity pledge data with columns:
                - symbol: Stock symbol
                - shareholder_name: Shareholder name
                - pledge_shares: Pledged shares (股)
                - pledge_ratio: Pledge ratio (%)
                - pledgee: Pledgee institution
                - pledge_date: Pledge date (YYYY-MM-DD)
        
        Raises:
            ValueError: If parameters are invalid
        
        Example:
            >>> provider = EastmoneyEquityPledgeProvider()
            >>> df = provider.get_equity_pledge('600000', '2024-01-01', '2024-01-31')
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)
        
        try:
            import akshare as ak
            
            if symbol:
                # Get pledge data for a specific stock
                # akshare function: stock_gpzy_pledge_ratio_detail_em(symbol: str = "000001")
                raw_df = ak.stock_gpzy_pledge_ratio_detail_em(symbol=symbol)
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'symbol', 'shareholder_name', 'pledge_shares', 
                        'pledge_ratio', 'pledgee', 'pledge_date'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                
                # Map columns based on akshare output
                if '股东名称' in raw_df.columns:
                    standardized['shareholder_name'] = raw_df['股东名称'].astype(str)
                else:
                    standardized['shareholder_name'] = ''
                
                # Set symbol for all rows
                standardized.insert(0, 'symbol', symbol.zfill(6))
                
                if '质押股数' in raw_df.columns:
                    standardized['pledge_shares'] = raw_df['质押股数'].astype(float)
                else:
                    standardized['pledge_shares'] = 0.0
                
                if '占所持股份比例' in raw_df.columns:
                    standardized['pledge_ratio'] = raw_df['占所持股份比例'].astype(float)
                elif '质押比例' in raw_df.columns:
                    standardized['pledge_ratio'] = raw_df['质押比例'].astype(float)
                else:
                    standardized['pledge_ratio'] = 0.0
                
                if '质权人' in raw_df.columns:
                    standardized['pledgee'] = raw_df['质权人'].astype(str)
                else:
                    standardized['pledgee'] = ''
                
                if '公告日期' in raw_df.columns:
                    standardized['pledge_date'] = pd.to_datetime(raw_df['公告日期']).dt.strftime('%Y-%m-%d')
                elif '质押日期' in raw_df.columns:
                    standardized['pledge_date'] = pd.to_datetime(raw_df['质押日期']).dt.strftime('%Y-%m-%d')
                else:
                    standardized['pledge_date'] = ''
                
                # Filter by date range
                if standardized['pledge_date'].iloc[0]:  # Check if date column has data
                    mask = (standardized['pledge_date'] >= start_date) & (standardized['pledge_date'] <= end_date)
                    result = standardized[mask].reset_index(drop=True)
                else:
                    result = standardized
                
            else:
                # Get pledge data for all stocks - use the ratio function which returns all stocks
                # akshare function: stock_gpzy_pledge_ratio_em()
                raw_df = ak.stock_gpzy_pledge_ratio_em()
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'symbol', 'shareholder_name', 'pledge_shares', 
                        'pledge_ratio', 'pledgee', 'pledge_date'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                
                if '股票代码' in raw_df.columns:
                    standardized['symbol'] = raw_df['股票代码'].astype(str).str.zfill(6)
                else:
                    standardized['symbol'] = ''
                
                if '股东名称' in raw_df.columns:
                    standardized['shareholder_name'] = raw_df['股东名称'].astype(str)
                else:
                    standardized['shareholder_name'] = ''
                
                if '质押股数' in raw_df.columns:
                    standardized['pledge_shares'] = raw_df['质押股数'].astype(float)
                else:
                    standardized['pledge_shares'] = 0.0
                
                if '占所持股份比例' in raw_df.columns:
                    standardized['pledge_ratio'] = raw_df['占所持股份比例'].astype(float)
                elif '质押比例' in raw_df.columns:
                    standardized['pledge_ratio'] = raw_df['质押比例'].astype(float)
                else:
                    standardized['pledge_ratio'] = 0.0
                
                if '质权人' in raw_df.columns:
                    standardized['pledgee'] = raw_df['质权人'].astype(str)
                else:
                    standardized['pledgee'] = ''
                
                if '公告日期' in raw_df.columns:
                    standardized['pledge_date'] = pd.to_datetime(raw_df['公告日期']).dt.strftime('%Y-%m-%d')
                elif '质押日期' in raw_df.columns:
                    standardized['pledge_date'] = pd.to_datetime(raw_df['质押日期']).dt.strftime('%Y-%m-%d')
                else:
                    standardized['pledge_date'] = ''
                
                # Filter by date range if date column has data
                if standardized['pledge_date'].iloc[0] if len(standardized) > 0 else False:
                    mask = (standardized['pledge_date'] >= start_date) & (standardized['pledge_date'] <= end_date)
                    result = standardized[mask].reset_index(drop=True)
                else:
                    result = standardized
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch equity pledge data: {e}") from e
    
    def get_equity_pledge_ratio_rank(
        self,
        date: str,
        top_n: int
    ) -> pd.DataFrame:
        """
        Get equity pledge ratio ranking from Eastmoney.
        
        Args:
            date: Query date (YYYY-MM-DD)
            top_n: Number of top stocks to return
        
        Returns:
            pd.DataFrame: Ranking data with columns:
                - rank: Ranking
                - symbol: Stock symbol
                - name: Stock name
                - pledge_ratio: Total pledge ratio (%)
                - pledge_value: Pledged market value (元)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD") from e
        
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")
        
        try:
            import akshare as ak
            
            # Get pledge ratio ranking
            # akshare function: stock_gpzy_pledge_ratio_em()
            raw_df = ak.stock_gpzy_pledge_ratio_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'rank', 'symbol', 'name', 'pledge_ratio', 'pledge_value'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            
            if '股票代码' in raw_df.columns:
                standardized['symbol'] = raw_df['股票代码'].astype(str).str.zfill(6)
            else:
                standardized['symbol'] = ''
            
            if '股票简称' in raw_df.columns:
                standardized['name'] = raw_df['股票简称'].astype(str)
            else:
                standardized['name'] = ''
            
            if '质押比例' in raw_df.columns:
                standardized['pledge_ratio'] = raw_df['质押比例'].astype(float)
            elif '质押率' in raw_df.columns:
                standardized['pledge_ratio'] = raw_df['质押率'].astype(float)
            else:
                standardized['pledge_ratio'] = 0.0
            
            if '质押市值' in raw_df.columns:
                standardized['pledge_value'] = raw_df['质押市值'].astype(float)
            else:
                standardized['pledge_value'] = 0.0
            
            # Sort by pledge ratio descending
            standardized = standardized.sort_values('pledge_ratio', ascending=False).reset_index(drop=True)
            
            # Add ranking
            standardized.insert(0, 'rank', range(1, len(standardized) + 1))
            
            # Limit to top_n
            result = standardized.head(top_n)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch equity pledge ratio ranking: {e}") from e
