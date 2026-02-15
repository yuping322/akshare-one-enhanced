"""
Eastmoney margin financing data provider.

This module implements the margin financing data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

from typing import Optional
import pandas as pd

from .base import MarginProvider


class EastmoneyMarginProvider(MarginProvider):
    """
    Margin financing data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch margin financing data from Eastmoney
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
    
    def get_margin_data(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get margin financing data from Eastmoney.
        
        This method wraps akshare margin financing functions and standardizes
        the output format.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized margin financing data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - margin_balance: Margin financing balance (元)
                - margin_buy: Margin financing buy amount (元)
                - short_balance: Short selling balance (元)
                - short_sell_volume: Short selling volume (股)
                - total_balance: Total margin balance (元)
        
        Raises:
            ValueError: If parameters are invalid
        
        Example:
            >>> provider = EastmoneyMarginProvider()
            >>> df = provider.get_margin_data('600000', '2024-01-01', '2024-01-31')
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)
        
        try:
            import akshare as ak
            
            if symbol:
                # Get margin data for a specific stock
                # Determine market based on symbol
                market = 'sse' if symbol.startswith('6') else 'szse'
                
                if market == 'sse':
                    # akshare function: stock_margin_detail_sse(date: str = '20230922')
                    # 使用最近的交易日期
                    from datetime import datetime
                    trade_date = datetime.now().strftime('%Y%m%d')
                    raw_df = ak.stock_margin_detail_sse(date=trade_date)
                    # 过滤指定股票
                    if not raw_df.empty and '标的证券代码' in raw_df.columns:
                        raw_df = raw_df[raw_df['标的证券代码'] == symbol]
                else:
                    # akshare function: stock_margin_detail_szse(date: str = "20230922")
                    # 使用最近的交易日期
                    from datetime import datetime
                    trade_date = datetime.now().strftime('%Y%m%d')
                    raw_df = ak.stock_margin_detail_szse(date=trade_date)
                    # 过滤指定股票
                    if not raw_df.empty and '标的证券代码' in raw_df.columns:
                        raw_df = raw_df[raw_df['标的证券代码'] == symbol]
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'date', 'symbol', 'name', 'margin_balance', 'margin_buy',
                        'short_balance', 'short_sell_volume', 'total_balance'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                standardized['date'] = pd.to_datetime(raw_df['信用交易日期']).dt.strftime('%Y-%m-%d')
                standardized['symbol'] = symbol.zfill(6)
                standardized['name'] = raw_df['股票简称'].iloc[0] if '股票简称' in raw_df.columns else ''
                standardized['margin_balance'] = raw_df['融资余额'].astype(float)
                standardized['margin_buy'] = raw_df['融资买入额'].astype(float)
                
                # Handle short selling columns (may not exist for all stocks)
                if '融券余额' in raw_df.columns:
                    standardized['short_balance'] = raw_df['融券余额'].astype(float)
                else:
                    standardized['short_balance'] = 0.0
                
                if '融券卖出量' in raw_df.columns:
                    standardized['short_sell_volume'] = raw_df['融券卖出量'].astype(float)
                else:
                    standardized['short_sell_volume'] = 0.0
                
                # Calculate total balance
                standardized['total_balance'] = standardized['margin_balance'] + standardized['short_balance']
                
                # Filter by date range
                mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
                result = standardized[mask].reset_index(drop=True)
                
            else:
                # Get margin data for all stocks
                # akshare function: stock_margin_underlying_info_szse(date: str = "20240101")
                # Note: Only Shenzhen has this function, Shanghai doesn't have a similar one
                from datetime import datetime
                
                # Use end_date as the query date
                date_str = end_date.replace('-', '')
                raw_df = ak.stock_margin_underlying_info_szse(date=date_str)
                
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'date', 'symbol', 'name', 'margin_balance', 'margin_buy',
                        'short_balance', 'short_sell_volume', 'total_balance'
                    ])
                
                # Standardize the data
                standardized = pd.DataFrame()
                standardized['date'] = end_date
                standardized['symbol'] = raw_df['标的代码'].astype(str).str.zfill(6)
                standardized['name'] = raw_df['标的简称'].astype(str)
                
                # Map columns based on available data
                if '融资余额' in raw_df.columns:
                    standardized['margin_balance'] = raw_df['融资余额'].astype(float)
                else:
                    standardized['margin_balance'] = 0.0
                
                # Margin buy amount may not be available in summary data
                standardized['margin_buy'] = 0.0
                
                if '融券余额' in raw_df.columns:
                    standardized['short_balance'] = raw_df['融券余额'].astype(float)
                else:
                    standardized['short_balance'] = 0.0
                
                standardized['short_sell_volume'] = 0.0
                standardized['total_balance'] = standardized['margin_balance'] + standardized['short_balance']
                
                result = standardized
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch margin financing data: {e}") from e
    
    def get_margin_summary(
        self,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """
        Get margin financing summary data from Eastmoney.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market ('sh', 'sz', or 'all')
        
        Returns:
            pd.DataFrame: Summary data with columns:
                - date: Date (YYYY-MM-DD)
                - market: Market ('sh', 'sz', or 'all')
                - margin_balance: Total margin financing balance (元)
                - short_balance: Total short selling balance (元)
                - total_balance: Total margin balance (元)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if market not in ['sh', 'sz', 'all']:
            raise ValueError(f"Invalid market: {market}. Must be 'sh', 'sz', or 'all'")
        
        try:
            import akshare as ak
            
            # Get margin summary data
            # akshare function: stock_margin_sse(date: str = "20240101") for Shanghai
            # akshare function: stock_margin_szse(date: str = "20240101") for Shenzhen
            
            results = []
            
            if market in ['sh', 'all']:
                # Get Shanghai market data
                # 使用最近的交易日期而不是start_date
                from datetime import datetime
                trade_date = datetime.now().strftime('%Y%m%d')
                raw_df_sh = ak.stock_margin_sse(date=trade_date)
                
                if not raw_df_sh.empty:
                    # Standardize Shanghai data
                    for _, row in raw_df_sh.iterrows():
                        date_str = pd.to_datetime(row['信用交易日期']).strftime('%Y-%m-%d')
                        if start_date <= date_str <= end_date:
                            results.append({
                                'date': date_str,
                                'market': 'sh',
                                'margin_balance': float(row['融资余额']) if '融资余额' in row else 0.0,
                                'short_balance': float(row['融券余额']) if '融券余额' in row else 0.0,
                                'total_balance': float(row['融资融券余额']) if '融资融券余额' in row else 0.0
                            })
            
            if market in ['sz', 'all']:
                # Get Shenzhen market data
                raw_df_sz = ak.stock_margin_szse(date=start_date.replace('-', ''))
                
                if not raw_df_sz.empty:
                    # Standardize Shenzhen data
                    for _, row in raw_df_sz.iterrows():
                        date_str = pd.to_datetime(row['信用交易日期']).strftime('%Y-%m-%d')
                        if start_date <= date_str <= end_date:
                            results.append({
                                'date': date_str,
                                'market': 'sz',
                                'margin_balance': float(row['融资余额']) if '融资余额' in row else 0.0,
                                'short_balance': float(row['融券余额']) if '融券余额' in row else 0.0,
                                'total_balance': float(row['融资融券余额']) if '融资融券余额' in row else 0.0
                            })
            
            if not results:
                return self.create_empty_dataframe([
                    'date', 'market', 'margin_balance', 'short_balance', 'total_balance'
                ])
            
            result_df = pd.DataFrame(results)
            
            # If market is 'all', aggregate Shanghai and Shenzhen data
            if market == 'all':
                # Group by date and sum the balances
                all_data = result_df.groupby('date').agg({
                    'margin_balance': 'sum',
                    'short_balance': 'sum',
                    'total_balance': 'sum'
                }).reset_index()
                all_data['market'] = 'all'
                
                # Combine with individual market data
                result_df = pd.concat([result_df, all_data], ignore_index=True)
            
            # Sort by date and market
            result_df = result_df.sort_values(['date', 'market']).reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result_df)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch margin financing summary: {e}") from e
