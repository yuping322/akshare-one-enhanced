"""
Eastmoney restricted stock release data provider.

This module implements the restricted release data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

from typing import Optional
import pandas as pd

from .base import RestrictedReleaseProvider


class EastmoneyRestrictedReleaseProvider(RestrictedReleaseProvider):
    """
    Restricted release data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch restricted release data from Eastmoney
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
    
    def get_restricted_release(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get restricted stock release data from Eastmoney.
        
        This method wraps akshare restricted release functions and standardizes
        the output format.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized restricted release data with columns:
                - symbol: Stock symbol
                - release_date: Release date (YYYY-MM-DD)
                - release_shares: Released shares (股)
                - release_value: Released market value (元)
                - release_type: Release type
                - shareholder_name: Shareholder name
        
        Raises:
            ValueError: If parameters are invalid
        
        Example:
            >>> provider = EastmoneyRestrictedReleaseProvider()
            >>> df = provider.get_restricted_release('600000', '2024-01-01', '2024-12-31')
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)
        
        try:
            import akshare as ak
            
            if symbol:
                # Get restricted release data for a specific stock
                # akshare function: stock_restricted_release_queue_em(symbol: str = "000001")
                raw_df = ak.stock_restricted_release_queue_em(symbol=symbol)
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'symbol', 'release_date', 'release_shares', 
                        'release_value', 'release_type', 'shareholder_name'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                
                # Map columns based on akshare output
                if '解禁时间' in raw_df.columns:
                    standardized['release_date'] = pd.to_datetime(raw_df['解禁时间']).dt.strftime('%Y-%m-%d')
                elif '上市日期' in raw_df.columns:
                    standardized['release_date'] = pd.to_datetime(raw_df['上市日期']).dt.strftime('%Y-%m-%d')
                else:
                    standardized['release_date'] = ''
                
                if '解禁数量' in raw_df.columns:
                    standardized['release_shares'] = raw_df['解禁数量'].astype(float)
                elif '实际解禁数量' in raw_df.columns:
                    standardized['release_shares'] = raw_df['实际解禁数量'].astype(float)
                else:
                    standardized['release_shares'] = 0.0
                
                if '解禁市值' in raw_df.columns:
                    standardized['release_value'] = raw_df['解禁市值'].astype(float)
                elif '实际解禁市值' in raw_df.columns:
                    standardized['release_value'] = raw_df['实际解禁市值'].astype(float)
                else:
                    standardized['release_value'] = 0.0
                
                if '股份类型' in raw_df.columns:
                    standardized['release_type'] = raw_df['股份类型'].astype(str)
                elif '限售股类型' in raw_df.columns:
                    standardized['release_type'] = raw_df['限售股类型'].astype(str)
                else:
                    standardized['release_type'] = ''
                
                if '股东名称' in raw_df.columns:
                    standardized['shareholder_name'] = raw_df['股东名称'].astype(str)
                else:
                    standardized['shareholder_name'] = ''
                
                # Set symbol for all rows at the end
                standardized.insert(0, 'symbol', symbol.zfill(6))
                
                # Filter by date range
                if standardized['release_date'].iloc[0]:  # Check if date column has data
                    mask = (standardized['release_date'] >= start_date) & (standardized['release_date'] <= end_date)
                    result = standardized[mask].reset_index(drop=True)
                else:
                    result = standardized
                
            else:
                # Get restricted release data for all stocks
                # akshare function: stock_restricted_release_summary_em(date: str = "20240101")
                # We need to fetch data for the date range
                # For simplicity, we'll use the detail function which returns all upcoming releases
                raw_df = ak.stock_restricted_release_detail_em()
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'symbol', 'release_date', 'release_shares', 
                        'release_value', 'release_type', 'shareholder_name'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                
                if '股票代码' in raw_df.columns:
                    standardized['symbol'] = raw_df['股票代码'].astype(str).str.zfill(6)
                else:
                    standardized['symbol'] = ''
                
                if '解禁时间' in raw_df.columns:
                    standardized['release_date'] = pd.to_datetime(raw_df['解禁时间']).dt.strftime('%Y-%m-%d')
                elif '上市日期' in raw_df.columns:
                    standardized['release_date'] = pd.to_datetime(raw_df['上市日期']).dt.strftime('%Y-%m-%d')
                else:
                    standardized['release_date'] = ''
                
                if '解禁数量' in raw_df.columns:
                    standardized['release_shares'] = raw_df['解禁数量'].astype(float)
                elif '实际解禁数量' in raw_df.columns:
                    standardized['release_shares'] = raw_df['实际解禁数量'].astype(float)
                else:
                    standardized['release_shares'] = 0.0
                
                if '解禁市值' in raw_df.columns:
                    standardized['release_value'] = raw_df['解禁市值'].astype(float)
                elif '实际解禁市值' in raw_df.columns:
                    standardized['release_value'] = raw_df['实际解禁市值'].astype(float)
                else:
                    standardized['release_value'] = 0.0
                
                if '股份类型' in raw_df.columns:
                    standardized['release_type'] = raw_df['股份类型'].astype(str)
                elif '限售股类型' in raw_df.columns:
                    standardized['release_type'] = raw_df['限售股类型'].astype(str)
                else:
                    standardized['release_type'] = ''
                
                if '股东名称' in raw_df.columns:
                    standardized['shareholder_name'] = raw_df['股东名称'].astype(str)
                else:
                    standardized['shareholder_name'] = ''
                
                # Filter by date range if date column has data
                if len(standardized) > 0 and standardized['release_date'].iloc[0]:
                    mask = (standardized['release_date'] >= start_date) & (standardized['release_date'] <= end_date)
                    result = standardized[mask].reset_index(drop=True)
                else:
                    result = standardized
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch restricted release data: {e}") from e
    
    def get_restricted_release_calendar(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get restricted stock release calendar from Eastmoney.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Calendar data with columns:
                - date: Release date (YYYY-MM-DD)
                - release_stock_count: Number of stocks with releases
                - total_release_value: Total release market value (元)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate date range
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Get detailed release data and aggregate by date
            raw_df = ak.stock_restricted_release_detail_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'release_stock_count', 'total_release_value'
                ])
            
            # Extract and standardize date column
            if '解禁时间' in raw_df.columns:
                raw_df['date'] = pd.to_datetime(raw_df['解禁时间']).dt.strftime('%Y-%m-%d')
            elif '上市日期' in raw_df.columns:
                raw_df['date'] = pd.to_datetime(raw_df['上市日期']).dt.strftime('%Y-%m-%d')
            else:
                return self.create_empty_dataframe([
                    'date', 'release_stock_count', 'total_release_value'
                ])
            
            # Extract market value column
            if '解禁市值' in raw_df.columns:
                raw_df['value'] = raw_df['解禁市值'].astype(float)
            elif '实际解禁市值' in raw_df.columns:
                raw_df['value'] = raw_df['实际解禁市值'].astype(float)
            else:
                raw_df['value'] = 0.0
            
            # Filter by date range
            mask = (raw_df['date'] >= start_date) & (raw_df['date'] <= end_date)
            filtered_df = raw_df[mask]
            
            if filtered_df.empty:
                return self.create_empty_dataframe([
                    'date', 'release_stock_count', 'total_release_value'
                ])
            
            # Aggregate by date
            calendar = filtered_df.groupby('date').agg(
                release_stock_count=('date', 'count'),
                total_release_value=('value', 'sum')
            ).reset_index()
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(calendar)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch restricted release calendar: {e}") from e
