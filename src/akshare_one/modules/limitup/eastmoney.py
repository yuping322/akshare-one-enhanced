"""
Eastmoney limit up/down data provider.

This module implements the limit up/down data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from .base import LimitUpDownProvider


class EastmoneyLimitUpDownProvider(LimitUpDownProvider):
    """
    Limit up/down data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch limit up/down data from Eastmoney
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
    
    def get_limit_up_pool(self, date: str) -> pd.DataFrame:
        """
        Get limit up pool data from Eastmoney.
        
        This method wraps akshare limit up pool functions and standardizes
        the output format.
        
        Args:
            date: Date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized limit up pool data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - close_price: Closing price
                - limit_up_time: Time when limit up occurred
                - open_count: Number of times limit up was broken
                - seal_amount: Sealing order amount
                - consecutive_days: Number of consecutive limit up days
                - reason: Reason for limit up
                - turnover_rate: Turnover rate
        
        Raises:
            ValueError: If parameters are invalid
        
        Example:
            >>> provider = EastmoneyLimitUpDownProvider()
            >>> df = provider.get_limit_up_pool('2024-01-01')
        """
        # Validate parameters
        self.validate_date(date)
        
        try:
            import akshare as ak
            
            # Call akshare function to get limit up pool
            # Note: akshare uses date format YYYYMMDD
            date_str = date.replace('-', '')
            raw_df = ak.stock_zt_pool_em(date=date_str)
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'name', 'close_price', 'limit_up_time',
                    'open_count', 'seal_amount', 'consecutive_days', 'reason', 'turnover_rate'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.Series([date] * len(raw_df))
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['名称'].astype(str)
            standardized['close_price'] = raw_df['最新价'].astype(float)
            
            # Handle limit_up_time - may have different column names
            if '涨停时间' in raw_df.columns:
                standardized['limit_up_time'] = raw_df['涨停时间'].astype(str)
            elif '首次封板时间' in raw_df.columns:
                standardized['limit_up_time'] = raw_df['首次封板时间'].astype(str)
            elif '最后封板时间' in raw_df.columns:
                standardized['limit_up_time'] = raw_df['最后封板时间'].astype(str)
            else:
                standardized['limit_up_time'] = ''
            
            # Handle open_count - may have different column names
            if '打开次数' in raw_df.columns:
                standardized['open_count'] = raw_df['打开次数'].astype(int)
            elif '炸板次数' in raw_df.columns:
                standardized['open_count'] = raw_df['炸板次数'].astype(int)
            else:
                standardized['open_count'] = 0
            
            # Handle seal_amount - may have different column names
            if '封单金额' in raw_df.columns:
                standardized['seal_amount'] = raw_df['封单金额'].astype(float)
            elif '封单额' in raw_df.columns:
                standardized['seal_amount'] = raw_df['封单额'].astype(float)
            elif '封板资金' in raw_df.columns:
                standardized['seal_amount'] = raw_df['封板资金'].astype(float)
            elif '封单资金' in raw_df.columns:
                standardized['seal_amount'] = raw_df['封单资金'].astype(float)
            else:
                standardized['seal_amount'] = None
            
            # Handle consecutive_days
            if '连板数' in raw_df.columns:
                standardized['consecutive_days'] = raw_df['连板数'].astype(int)
            elif '连续涨停' in raw_df.columns:
                standardized['consecutive_days'] = raw_df['连续涨停'].astype(int)
            else:
                standardized['consecutive_days'] = 1
            
            # Handle reason
            if '涨停原因' in raw_df.columns:
                standardized['reason'] = raw_df['涨停原因'].astype(str)
            elif '所属行业' in raw_df.columns:
                standardized['reason'] = raw_df['所属行业'].astype(str)
            else:
                standardized['reason'] = ''
            
            standardized['turnover_rate'] = raw_df['换手率'].astype(float)
            
            # Ensure JSON compatibility
            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch limit up pool data: {e}") from e
    
    def get_limit_down_pool(self, date: str) -> pd.DataFrame:
        """
        Get limit down pool data from Eastmoney.
        
        Args:
            date: Date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized limit down pool data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - close_price: Closing price
                - limit_down_time: Time when limit down occurred
                - open_count: Number of times limit down was broken
                - turnover_rate: Turnover rate
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date(date)
        
        try:
            import akshare as ak
            
            # Call akshare function to get limit down pool
            # Note: akshare uses date format YYYYMMDD
            date_str = date.replace('-', '')
            raw_df = ak.stock_zt_pool_dtgc_em(date=date_str)
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'name', 'close_price', 'limit_down_time',
                    'open_count', 'turnover_rate'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.Series([date] * len(raw_df))
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['名称'].astype(str)
            standardized['close_price'] = raw_df['最新价'].astype(float)
            
            # Handle limit_down_time - may have different column names
            if '跌停时间' in raw_df.columns:
                standardized['limit_down_time'] = raw_df['跌停时间'].astype(str)
            elif '最后封板时间' in raw_df.columns:
                standardized['limit_down_time'] = raw_df['最后封板时间'].astype(str)
            else:
                standardized['limit_down_time'] = ''
            
            # Handle open_count - may have different column names
            if '打开次数' in raw_df.columns:
                standardized['open_count'] = raw_df['打开次数'].astype(int)
            elif '开板次数' in raw_df.columns:
                standardized['open_count'] = raw_df['开板次数'].astype(int)
            else:
                standardized['open_count'] = 0
            
            standardized['turnover_rate'] = raw_df['换手率'].astype(float)
            
            # Ensure JSON compatibility
            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch limit down pool data: {e}") from e
    
    def get_limit_up_stats(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get limit up/down statistics from Eastmoney.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Statistics with columns:
                - date: Date (YYYY-MM-DD)
                - limit_up_count: Number of limit up stocks
                - limit_down_count: Number of limit down stocks
                - broken_rate: Rate of broken limit ups (%)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            from datetime import datetime, timedelta
            
            # Generate date range
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            results = []
            current = start
            
            while current <= end:
                date_str = current.strftime('%Y%m%d')
                date_display = current.strftime('%Y-%m-%d')
                
                try:
                    # Get limit up pool
                    limit_up_df = ak.stock_zt_pool_em(date=date_str)
                    limit_up_count = len(limit_up_df) if not limit_up_df.empty else 0
                    
                    # Calculate broken rate (stocks that opened after limit up)
                    if not limit_up_df.empty:
                        if '打开次数' in limit_up_df.columns:
                            broken_count = (limit_up_df['打开次数'] > 0).sum()
                        elif '炸板次数' in limit_up_df.columns:
                            broken_count = (limit_up_df['炸板次数'] > 0).sum()
                        else:
                            broken_count = 0
                        broken_rate = (broken_count / limit_up_count * 100) if limit_up_count > 0 else 0.0
                    else:
                        broken_rate = 0.0
                    
                    # Get limit down pool
                    limit_down_df = ak.stock_zt_pool_dtgc_em(date=date_str)
                    limit_down_count = len(limit_down_df) if not limit_down_df.empty else 0
                    
                    results.append({
                        'date': date_display,
                        'limit_up_count': limit_up_count,
                        'limit_down_count': limit_down_count,
                        'broken_rate': broken_rate
                    })
                    
                except Exception:
                    # If data not available for this date, add zeros
                    results.append({
                        'date': date_display,
                        'limit_up_count': 0,
                        'limit_down_count': 0,
                        'broken_rate': 0.0
                    })
                
                current += timedelta(days=1)
            
            if not results:
                return self.create_empty_dataframe([
                    'date', 'limit_up_count', 'limit_down_count', 'broken_rate'
                ])
            
            result_df = pd.DataFrame(results)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result_df)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch limit up/down statistics: {e}") from e
