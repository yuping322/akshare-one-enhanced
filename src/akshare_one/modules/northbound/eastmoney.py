"""
Eastmoney provider for northbound capital data.

This module implements the northbound capital data provider using Eastmoney as the data source.
"""

import pandas as pd
import akshare as ak
from typing import Optional

from .base import NorthboundProvider


class EastmoneyNorthboundProvider(NorthboundProvider):
    """
    Eastmoney implementation of northbound capital data provider.
    
    Uses akshare's stock_hsgt_* functions to fetch northbound capital data.
    """
    
    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'eastmoney'
    
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Eastmoney.
        
        This method is not used directly; specific methods fetch their own data.
        """
        return pd.DataFrame()
    
    def get_northbound_flow(
        self,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """
        Get northbound capital flow data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market type ('sh', 'sz', or 'all')
        
        Returns:
            pd.DataFrame: Standardized northbound flow data
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        
        if market not in ['sh', 'sz', 'all']:
            raise ValueError(f"Invalid market: {market}. Must be 'sh', 'sz', or 'all'")
        
        try:
            # Fetch data using akshare
            # stock_hsgt_hist_em returns historical northbound flow data
            raw_df = ak.stock_hsgt_hist_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'market', 'net_buy', 'buy_amount', 'sell_amount', 'balance'
                ])
            
            # Standardize the data
            return self._standardize_flow_data(raw_df, start_date, end_date, market)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch northbound flow data: {e}") from e
    
    def _standardize_flow_data(
        self,
        df: pd.DataFrame,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """Standardize northbound flow data."""
        standardized = pd.DataFrame()
        
        # Map fields based on akshare output
        # New columns: 日期, 当日成交净买额, 买入成交额, 卖出成交额, 当日余额, etc.
        standardized['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        standardized['market'] = market
        
        # Use 当日成交净买额 (daily net buy amount) as net_buy
        # Convert from 亿元 to 亿元 (already in correct unit)
        if '当日成交净买额' in df.columns:
            standardized['net_buy'] = df['当日成交净买额'].astype(float)
        else:
            standardized['net_buy'] = None
        
        # Buy and sell amounts
        if '买入成交额' in df.columns:
            standardized['buy_amount'] = df['买入成交额'].astype(float)
        else:
            standardized['buy_amount'] = None
            
        if '卖出成交额' in df.columns:
            standardized['sell_amount'] = df['卖出成交额'].astype(float)
        else:
            standardized['sell_amount'] = None
        
        # Balance
        if '当日余额' in df.columns:
            standardized['balance'] = df['当日余额'].astype(float)
        else:
            standardized['balance'] = None
        
        # Filter by date range
        mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
        result = standardized[mask].reset_index(drop=True)
        
        return self.ensure_json_compatible(result)
    
    def get_northbound_holdings(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get northbound holdings details.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized northbound holdings data
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol is not None:
            self.validate_symbol(symbol)
        
        try:
            if symbol:
                # Fetch individual stock holdings
                raw_df = ak.stock_hsgt_individual_em(symbol=symbol)
            else:
                # Fetch all stocks holdings (use stock_hsgt_hold_stock_em)
                raw_df = ak.stock_hsgt_hold_stock_em(market="北向")
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'holdings_shares', 'holdings_value',
                    'holdings_ratio', 'holdings_change'
                ])
            
            # Standardize the data
            return self._standardize_holdings_data(raw_df, symbol, start_date, end_date)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch northbound holdings data: {e}") from e
    
    def _standardize_holdings_data(
        self,
        df: pd.DataFrame,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Standardize northbound holdings data."""
        standardized = pd.DataFrame()
        
        # Map fields based on akshare output
        if '日期' in df.columns:
            standardized['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        elif '持股日期' in df.columns:
            standardized['date'] = pd.to_datetime(df['持股日期']).dt.strftime('%Y-%m-%d')
        else:
            # If no date column, use current date
            standardized['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # Symbol
        if symbol:
            standardized['symbol'] = symbol
        elif '代码' in df.columns:
            standardized['symbol'] = df['代码'].astype(str).str.zfill(6)
        elif '股票代码' in df.columns:
            standardized['symbol'] = df['股票代码'].astype(str).str.zfill(6)
        else:
            standardized['symbol'] = None
        
        # Holdings shares
        if '持股数量' in df.columns:
            standardized['holdings_shares'] = df['持股数量'].astype(float)
        elif '持股数量(股)' in df.columns:
            standardized['holdings_shares'] = df['持股数量(股)'].astype(float)
        else:
            standardized['holdings_shares'] = None
        
        # Holdings value
        if '持股市值' in df.columns:
            standardized['holdings_value'] = df['持股市值'].astype(float)
        elif '持股市值(元)' in df.columns:
            standardized['holdings_value'] = df['持股市值(元)'].astype(float)
        else:
            standardized['holdings_value'] = None
        
        # Holdings ratio
        if '持股占比' in df.columns:
            standardized['holdings_ratio'] = df['持股占比'].astype(float)
        elif '持股占比(%)' in df.columns:
            standardized['holdings_ratio'] = df['持股占比(%)'].astype(float)
        else:
            standardized['holdings_ratio'] = None
        
        # Holdings change
        if '持股变化' in df.columns:
            standardized['holdings_change'] = df['持股变化'].astype(float)
        elif '持股数量增减' in df.columns:
            standardized['holdings_change'] = df['持股数量增减'].astype(float)
        else:
            standardized['holdings_change'] = None
        
        # Filter by date range if date column exists
        if 'date' in standardized.columns and standardized['date'].notna().any():
            mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
            result = standardized[mask].reset_index(drop=True)
        else:
            result = standardized
        
        return self.ensure_json_compatible(result)
    
    def get_northbound_top_stocks(
        self,
        date: str,
        market: str,
        top_n: int
    ) -> pd.DataFrame:
        """
        Get northbound capital top stocks ranking.
        
        Args:
            date: Date (YYYY-MM-DD)
            market: Market type ('sh', 'sz', or 'all')
            top_n: Number of top stocks to return
        
        Returns:
            pd.DataFrame: Ranked northbound holdings data
        """
        # Validate parameters
        self.validate_date(date)
        
        if market not in ['sh', 'sz', 'all']:
            raise ValueError(f"Invalid market: {market}. Must be 'sh', 'sz', or 'all'")
        
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")
        
        try:
            # Fetch stock statistics data using akshare
            # stock_hsgt_stock_statistics_em returns northbound holdings for individual stocks
            # Convert date format from YYYY-MM-DD to YYYYMMDD
            date_str = date.replace('-', '')
            raw_df = ak.stock_hsgt_stock_statistics_em(
                symbol="北向持股",
                start_date=date_str,
                end_date=date_str
            )
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'rank', 'symbol', 'name', 'net_buy', 'holdings_shares', 'holdings_ratio'
                ])
            
            # Standardize and limit to top_n
            return self._standardize_ranking_data(raw_df, market, top_n)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch northbound top stocks: {e}") from e
    
    def _standardize_ranking_data(self, df: pd.DataFrame, market: str, top_n: int) -> pd.DataFrame:
        """Standardize northbound ranking data."""
        standardized = pd.DataFrame()
        
        # Filter by market if needed (based on stock code prefix)
        if market == 'sh':
            # Shanghai stocks start with 6
            df = df[df['股票代码'].astype(str).str.startswith('6')]
        elif market == 'sz':
            # Shenzhen stocks start with 0 or 3
            df = df[df['股票代码'].astype(str).str.match(r'^[03]')]
        # else 'all' - no filtering needed
        
        # Sort by holdings value (持股市值) in descending order
        if '持股市值' in df.columns:
            df = df.sort_values('持股市值', ascending=False)
        
        # Add ranking
        standardized['rank'] = range(1, len(df) + 1)
        
        # Map fields - new column names from stock_hsgt_stock_statistics_em
        if '股票代码' in df.columns:
            standardized['symbol'] = df['股票代码'].astype(str).str.zfill(6)
        else:
            standardized['symbol'] = None
        
        if '股票简称' in df.columns:
            standardized['name'] = df['股票简称'].astype(str)
        else:
            standardized['name'] = None
        
        # Net buy amount - use 持股市值变化-1日 (1-day holdings value change)
        if '持股市值变化-1日' in df.columns:
            # Convert from yuan to yi yuan (亿元)
            standardized['net_buy'] = df['持股市值变化-1日'].astype(float) / 100000000
        else:
            standardized['net_buy'] = None
        
        # Holdings shares
        if '持股数量' in df.columns:
            standardized['holdings_shares'] = df['持股数量'].astype(float)
        else:
            standardized['holdings_shares'] = None
        
        # Holdings ratio
        if '持股数量占发行股百分比' in df.columns:
            standardized['holdings_ratio'] = df['持股数量占发行股百分比'].astype(float)
        else:
            standardized['holdings_ratio'] = None
        
        # Limit to top_n
        result = standardized.head(top_n).reset_index(drop=True)
        
        # Re-rank after filtering
        result['rank'] = range(1, len(result) + 1)
        
        return self.ensure_json_compatible(result)
