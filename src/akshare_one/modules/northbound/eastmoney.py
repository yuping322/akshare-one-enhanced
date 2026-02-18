"""
Eastmoney provider for northbound capital data.

This module implements the northbound capital data provider using Eastmoney as the data source.
"""


import akshare as ak
import pandas as pd

from ..field_naming import FieldType
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
        # Convert from 亿元 to 元
        if '当日成交净买额' in df.columns:
            # Convert from 亿元 (hundred million yuan) to 元 (yuan)
            standardized['net_buy'] = df['当日成交净买额'].astype(float) * 100000000
        else:
            standardized['net_buy'] = None
        
        # Buy and sell amounts
        if '买入成交额' in df.columns:
            # Convert from 亿元 (hundred million yuan) to 元 (yuan)
            standardized['buy_amount'] = df['买入成交额'].astype(float) * 100000000
        else:
            standardized['buy_amount'] = None
            
        if '卖出成交额' in df.columns:
            # Convert from 亿元 (hundred million yuan) to 元 (yuan)
            standardized['sell_amount'] = df['卖出成交额'].astype(float) * 100000000
        else:
            standardized['sell_amount'] = None
        
        # Balance
        if '当日余额' in df.columns:
            # Convert from 亿元 (hundred million yuan) to 元 (yuan)
            standardized['balance'] = df['当日余额'].astype(float) * 100000000
        else:
            standardized['balance'] = None
        
        # Filter by date range
        mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
        result = standardized[mask].reset_index(drop=True)
        
        # Define field types for validation
        field_types = {
            'date': FieldType.DATE,
            'market': FieldType.MARKET,
            'northbound_net_buy': FieldType.NET_FLOW,
            'northbound_buy_amount': FieldType.AMOUNT,
            'northbound_sell_amount': FieldType.AMOUNT,
            'northbound_balance': FieldType.BALANCE
        }
        
        # Apply field name validation if available
        try:
            result = self.apply_field_standardization(result, field_types)
        except Exception:
            # If validation fails, return the result as is
            pass
        
        return self.ensure_json_compatible(result)
    
    def get_northbound_holdings(
        self,
        symbol: str | None,
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
        symbol: str | None,
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
            # Convert from 元 (yuan) to 元 (yuan)
            standardized['holdings_value'] = df['持股市值'].astype(float)
        elif '持股市值(元)' in df.columns:
            # Convert from 元 (yuan) to 元 (yuan)
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
        
        # Define field types for validation
        field_types = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL,
            'holdings_shares': FieldType.SHARES,
            'holdings_value': FieldType.VALUE,
            'holdings_ratio': FieldType.RATIO,
            'holdings_change': FieldType.SHARES
        }
        
        # Apply field name validation if available
        try:
            result = self.apply_field_standardization(result, field_types)
        except Exception:
            # If validation fails, return the result as is
            pass
        
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
            # Use stock_hsgt_hold_stock_em as the data source
            # This API returns current northbound holdings for all stocks
            raw_df = ak.stock_hsgt_hold_stock_em(market="北向")
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'rank', 'symbol', 'name', 'net_buy', 'holdings_shares', 'holdings_ratio'
                ])
            
            # Standardize and limit to top_n
            return self._standardize_ranking_data(raw_df, market, top_n, date)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch northbound top stocks: {e}") from e
    
    def _standardize_ranking_data(self, df: pd.DataFrame, market: str, top_n: int, date: str | None = None) -> pd.DataFrame:
        """Standardize northbound ranking data.
        
        Args:
            df: Raw DataFrame from stock_hsgt_hold_stock_em
            market: Market filter ('sh', 'sz', or 'all')
            top_n: Number of top stocks to return
            date: Optional date filter (YYYY-MM-DD)
        """
        standardized = pd.DataFrame()
        
        # Filter by market if needed (based on stock code prefix)
        # Column '代码' contains stock codes from stock_hsgt_hold_stock_em
        code_col = '代码' if '代码' in df.columns else '股票代码'
        
        if market == 'sh':
            # Shanghai stocks start with 6
            df = df[df[code_col].astype(str).str.startswith('6')]
        elif market == 'sz':
            # Shenzhen stocks start with 0 or 3
            df = df[df[code_col].astype(str).str.match(r'^[03]')]
        # else 'all' - no filtering needed
        
        # Sort by holdings value (今日持股-市值) in descending order
        value_col = '今日持股-市值' if '今日持股-市值' in df.columns else '持股市值'
        if value_col in df.columns:
            df = df.sort_values(value_col, ascending=False)
        
        # Add ranking
        standardized['rank'] = range(1, len(df) + 1)
        
        # Map fields - column names from stock_hsgt_hold_stock_em
        if code_col in df.columns:
            standardized['symbol'] = df[code_col].astype(str).str.zfill(6)
        else:
            standardized['symbol'] = None
        
        name_col = '名称' if '名称' in df.columns else '股票简称'
        if name_col in df.columns:
            standardized['name'] = df[name_col].astype(str)
        else:
            standardized['name'] = None
        
        # Net buy amount - use 5日增持估计-市值 (5-day estimated holdings increase)
        # or 持股市值变化-1日 (1-day holdings value change)
        if '5日增持估计-市值' in df.columns:
            standardized['northbound_net_buy'] = pd.to_numeric(df['5日增持估计-市值'], errors='coerce')
        elif '持股市值变化-1日' in df.columns:
            standardized['northbound_net_buy'] = pd.to_numeric(df['持股市值变化-1日'], errors='coerce') / 100000000
        else:
            standardized['northbound_net_buy'] = None
        
        # Holdings shares
        shares_col = '今日持股-股数' if '今日持股-股数' in df.columns else '持股数量'
        if shares_col in df.columns:
            standardized['holdings_shares'] = pd.to_numeric(df[shares_col], errors='coerce')
        else:
            standardized['holdings_shares'] = None
        
        # Holdings ratio
        ratio_col = '今日持股-占流通股比' if '今日持股-占流通股比' in df.columns else '持股数量占发行股百分比'
        if ratio_col in df.columns:
            standardized['holdings_ratio'] = pd.to_numeric(df[ratio_col], errors='coerce')
        else:
            standardized['holdings_ratio'] = None
        
        # Add date if available
        if date:
            standardized['date'] = date
        elif '日期' in df.columns:
            standardized['date'] = df['日期'].astype(str)
        
        # Limit to top_n
        result = standardized.head(top_n).reset_index(drop=True)
        
        # Re-rank after filtering
        result['rank'] = range(1, len(result) + 1)
        
        # Define field types for validation
        field_types = {
            'rank': FieldType.RANK,
            'symbol': FieldType.SYMBOL,
            'name': FieldType.NAME,
            'northbound_net_buy': FieldType.NET_FLOW,
            'holdings_shares': FieldType.SHARES,
            'holdings_ratio': FieldType.RATIO
        }
        
        # Apply field name validation if available
        try:
            result = self.apply_field_standardization(result, field_types)
        except Exception:
            # If validation fails, return the result as is
            pass
        
        return self.ensure_json_compatible(result)
