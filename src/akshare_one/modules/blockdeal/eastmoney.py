"""
Eastmoney block deal data provider.

This module implements the block deal data provider using Eastmoney as the data source.
"""

import pandas as pd

from .base import BlockDealProvider


class EastmoneyBlockDealProvider(BlockDealProvider):
    """
    Block deal data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch block deal data from Eastmoney
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
    
    def get_block_deal(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get block deal transaction details from Eastmoney.
        
        Args:
            symbol: Stock symbol (6-digit code). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized block deal data
        """
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)
        
        try:
            import akshare as ak
            
            # Call akshare function
            if symbol:
                raw_df = ak.stock_dzjy_mrmx(symbol=symbol)
            else:
                # Get market-wide data - akshare的stock_dzjy_sctj不接受参数
                raw_df = ak.stock_dzjy_sctj()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'name', 'price', 'volume', 'amount',
                    'buyer_branch', 'seller_branch', 'premium_rate'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['date'] = pd.to_datetime(raw_df['交易日期']).dt.strftime('%Y-%m-%d')
            standardized['symbol'] = raw_df['证券代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['证券简称'].astype(str)
            standardized['price'] = raw_df['成交价'].astype(float)
            standardized['volume'] = raw_df['成交量'].astype(float)
            standardized['amount'] = raw_df['成交额'].astype(float)
            standardized['buyer_branch'] = raw_df['买方营业部'].astype(str)
            standardized['seller_branch'] = raw_df['卖方营业部'].astype(str)
            
            # Calculate premium rate if close price is available
            if '收盘价' in raw_df.columns:
                close_price = raw_df['收盘价'].astype(float)
                standardized['premium_rate'] = ((standardized['price'] - close_price) / close_price * 100)
            else:
                standardized['premium_rate'] = None
            
            # Filter by date range
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch block deal data: {e}") from e
    
    def get_block_deal_summary(
        self,
        start_date: str,
        end_date: str,
        group_by: str
    ) -> pd.DataFrame:
        """
        Get block deal summary statistics from Eastmoney.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'date', or 'broker')
        
        Returns:
            pd.DataFrame: Summary statistics
        
        Raises:
            ValueError: If group_by is invalid
        """
        self.validate_date_range(start_date, end_date)
        
        if group_by not in ['stock', 'date', 'broker']:
            raise ValueError(
                f"Invalid group_by: {group_by}. "
                "Must be 'stock', 'date', or 'broker'"
            )
        
        try:
            # First get all block deal data
            all_data = self.get_block_deal(None, start_date, end_date)
            
            if all_data.empty:
                if group_by == 'stock':
                    return self.create_empty_dataframe([
                        'symbol', 'name', 'deal_count', 'total_amount', 'avg_premium_rate'
                    ])
                elif group_by == 'date':
                    return self.create_empty_dataframe([
                        'date', 'deal_count', 'total_amount', 'avg_premium_rate'
                    ])
                else:  # broker
                    return self.create_empty_dataframe([
                        'broker_name', 'deal_count', 'total_amount', 'avg_premium_rate'
                    ])
            
            # Group and aggregate based on group_by parameter
            if group_by == 'stock':
                summary = all_data.groupby(['symbol', 'name']).agg({
                    'amount': ['count', 'sum'],
                    'premium_rate': 'mean'
                }).reset_index()
                summary.columns = ['symbol', 'name', 'deal_count', 'total_amount', 'avg_premium_rate']
            
            elif group_by == 'date':
                summary = all_data.groupby('date').agg({
                    'amount': ['count', 'sum'],
                    'premium_rate': 'mean'
                }).reset_index()
                summary.columns = ['date', 'deal_count', 'total_amount', 'avg_premium_rate']
            
            else:  # broker
                # Combine buyer and seller branches
                buyer_summary = all_data.groupby('buyer_branch').agg({
                    'amount': ['count', 'sum'],
                    'premium_rate': 'mean'
                }).reset_index()
                buyer_summary.columns = ['broker_name', 'deal_count', 'total_amount', 'avg_premium_rate']
                
                seller_summary = all_data.groupby('seller_branch').agg({
                    'amount': ['count', 'sum'],
                    'premium_rate': 'mean'
                }).reset_index()
                seller_summary.columns = ['broker_name', 'deal_count', 'total_amount', 'avg_premium_rate']
                
                # Combine and aggregate
                summary = pd.concat([buyer_summary, seller_summary]).groupby('broker_name').agg({
                    'deal_count': 'sum',
                    'total_amount': 'sum',
                    'avg_premium_rate': 'mean'
                }).reset_index()
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(summary)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch block deal summary: {e}") from e
