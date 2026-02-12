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
        # Typical columns: 日期, 沪股通(亿元), 深股通(亿元), 北向资金(亿元), etc.
        standardized['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        if market == 'sh':
            standardized['market'] = 'sh'
            standardized['net_buy'] = df['沪股通(亿元)'].astype(float)
            standardized['buy_amount'] = None
            standardized['sell_amount'] = None
            standardized['balance'] = None
        elif market == 'sz':
            standardized['market'] = 'sz'
            standardized['net_buy'] = df['深股通(亿元)'].astype(float)
            standardized['buy_amount'] = None
            standardized['sell_amount'] = None
            standardized['balance'] = None
        else:  # 'all'
            standardized['market'] = 'all'
            standardized['net_buy'] = df['北向资金(亿元)'].astype(float) if '北向资金(亿元)' in df.columns else (
                df['沪股通(亿元)'].astype(float) + df['深股通(亿元)'].astype(float)
            )
            standardized['buy_amount'] = None
            standardized['sell_amount'] = None
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
            # Fetch ranking data using akshare
            # stock_hsgt_board_rank_em returns northbound holdings ranking
            if market == 'sh':
                raw_df = ak.stock_hsgt_board_rank_em(symbol="北向", indicator="沪股通")
            elif market == 'sz':
                raw_df = ak.stock_hsgt_board_rank_em(symbol="北向", indicator="深股通")
            else:  # 'all'
                raw_df = ak.stock_hsgt_board_rank_em(symbol="北向", indicator="北向")
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'rank', 'symbol', 'name', 'net_buy', 'holdings_shares', 'holdings_ratio'
                ])
            
            # Standardize and limit to top_n
            return self._standardize_ranking_data(raw_df, top_n)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch northbound top stocks: {e}") from e
    
    def _standardize_ranking_data(self, df: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """Standardize northbound ranking data."""
        standardized = pd.DataFrame()
        
        # Add ranking
        standardized['rank'] = range(1, len(df) + 1)
        
        # Map fields
        if '代码' in df.columns:
            standardized['symbol'] = df['代码'].astype(str).str.zfill(6)
        elif '股票代码' in df.columns:
            standardized['symbol'] = df['股票代码'].astype(str).str.zfill(6)
        else:
            standardized['symbol'] = None
        
        if '名称' in df.columns:
            standardized['name'] = df['名称'].astype(str)
        elif '股票名称' in df.columns:
            standardized['name'] = df['股票名称'].astype(str)
        else:
            standardized['name'] = None
        
        # Net buy amount
        if '今日持股' in df.columns:
            standardized['net_buy'] = df['今日持股'].astype(float)
        elif '今日净买入' in df.columns:
            standardized['net_buy'] = df['今日净买入'].astype(float)
        else:
            standardized['net_buy'] = None
        
        # Holdings shares
        if '持股数量' in df.columns:
            standardized['holdings_shares'] = df['持股数量'].astype(float)
        elif '持股数量(股)' in df.columns:
            standardized['holdings_shares'] = df['持股数量(股)'].astype(float)
        else:
            standardized['holdings_shares'] = None
        
        # Holdings ratio
        if '持股占比' in df.columns:
            standardized['holdings_ratio'] = df['持股占比'].astype(float)
        elif '持股占比(%)' in df.columns:
            standardized['holdings_ratio'] = df['持股占比(%)'].astype(float)
        else:
            standardized['holdings_ratio'] = None
        
        # Limit to top_n
        result = standardized.head(top_n).reset_index(drop=True)
        
        return self.ensure_json_compatible(result)
