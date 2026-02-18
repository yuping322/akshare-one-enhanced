"""
Eastmoney fund flow data provider.

This module implements the fund flow data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from ..field_naming import FieldType
from .base import FundFlowProvider


class EastmoneyFundFlowProvider(FundFlowProvider):
    """
    Fund flow data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch fund flow data from Eastmoney
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
    
    def get_stock_fund_flow(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get individual stock fund flow data from Eastmoney with full standardization.
        
        This method uses the enhanced standardization framework to ensure
        consistent field naming and data formatting.
        
        Args:
            symbol: Stock symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Fully standardized fund flow data with validated field names
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Determine market based on symbol prefix
            market = 'sh' if symbol.startswith('6') else 'sz'
            
            # Call akshare function
            raw_df = ak.stock_individual_fund_flow(stock=symbol, market=market)
            
            if raw_df.empty:
                # Return empty DataFrame with standardized columns
                return self.create_empty_dataframe([
                    'date', 'symbol', 'close_price', 'pct_change',
                    'fundflow_main_net_inflow', 'fundflow_main_net_inflow_rate',
                    'fundflow_super_large_net_inflow', 'fundflow_large_net_inflow',
                    'fundflow_medium_net_inflow', 'fundflow_small_net_inflow'
                ])
            
            # Use enhanced standardization framework
            standardized_df = self.get_data_with_full_standardization(
                apply_field_validation=True,
                field_types={
                    'fundflow_main_net_inflow': FieldType.NET_FLOW,
                    'fundflow_main_net_inflow_rate': FieldType.RATE,
                    'fundflow_super_large_net_inflow': FieldType.NET_FLOW,
                    'fundflow_large_net_inflow': FieldType.NET_FLOW,
                    'fundflow_medium_net_inflow': FieldType.NET_FLOW,
                    'fundflow_small_net_inflow': FieldType.NET_FLOW
                },
                amount_fields={
                    'fundflow_main_net_inflow': 'yuan',
                    'fundflow_super_large_net_inflow': 'yuan',
                    'fundflow_large_net_inflow': 'yuan',
                    'fundflow_medium_net_inflow': 'yuan',
                    'fundflow_small_net_inflow': 'yuan'
                }
            )
            
            # Apply custom field mapping for fund flow data
            if not standardized_df.empty:
                # Map raw data to standardized fields
                standardized_df['date'] = pd.to_datetime(raw_df['日期']).dt.strftime('%Y-%m-%d')
                standardized_df['symbol'] = symbol
                standardized_df['close_price'] = raw_df['收盘价'].astype(float)
                standardized_df['pct_change'] = raw_df['涨跌幅'].astype(float)
                standardized_df['fundflow_main_net_inflow'] = raw_df['主力净流入-净额'].astype(float)
                standardized_df['fundflow_main_net_inflow_rate'] = raw_df['主力净流入-净占比'].astype(float)
                standardized_df['fundflow_super_large_net_inflow'] = raw_df['超大单净流入-净额'].astype(float)
                standardized_df['fundflow_large_net_inflow'] = raw_df['大单净流入-净额'].astype(float)
                standardized_df['fundflow_medium_net_inflow'] = raw_df['中单净流入-净额'].astype(float)
                standardized_df['fundflow_small_net_inflow'] = raw_df['小单净流入-净额'].astype(float)
                
                # Filter by date range
                mask = (standardized_df['date'] >= start_date) & (standardized_df['date'] <= end_date)
                result = standardized_df[mask].reset_index(drop=True)
                
                return self.ensure_json_compatible(result)
            else:
                # Fallback to manual standardization if framework fails
                return self._manual_standardize_fundflow(raw_df, symbol, start_date, end_date)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch stock fund flow data: {e}") from e
    
    def _manual_standardize_fundflow(
        self, 
        raw_df: pd.DataFrame, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Manual standardization fallback method"""
        standardized = pd.DataFrame()
        standardized['date'] = pd.to_datetime(raw_df['日期']).dt.strftime('%Y-%m-%d')
        standardized['symbol'] = symbol
        standardized['close_price'] = raw_df['收盘价'].astype(float)
        standardized['pct_change'] = raw_df['涨跌幅'].astype(float)
        standardized['fundflow_main_net_inflow'] = raw_df['主力净流入-净额'].astype(float)
        standardized['fundflow_main_net_inflow_rate'] = raw_df['主力净流入-净占比'].astype(float)
        standardized['fundflow_super_large_net_inflow'] = raw_df['超大单净流入-净额'].astype(float)
        standardized['fundflow_large_net_inflow'] = raw_df['大单净流入-净额'].astype(float)
        standardized['fundflow_medium_net_inflow'] = raw_df['中单净流入-净额'].astype(float)
        standardized['fundflow_small_net_inflow'] = raw_df['小单净流入-净额'].astype(float)
        
        # Filter by date range
        mask = (standardized['date'] >= start_date) & (standardized['date'] <= end_date)
        result = standardized[mask].reset_index(drop=True)
        
        return self.ensure_json_compatible(result)
    
    def get_sector_fund_flow(
        self,
        sector_type: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get sector fund flow data from Eastmoney.
        
        Args:
            sector_type: Sector type ('industry' or 'concept')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized sector fund flow data
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if sector_type not in ['industry', 'concept']:
            raise ValueError(f"Invalid sector_type: {sector_type}. Must be 'industry' or 'concept'")
        self.validate_date_range(start_date, end_date)
        
        try:
            import akshare as ak
            
            # Call appropriate akshare function based on sector type
            if sector_type == 'industry':
                raw_df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
            else:  # concept
                raw_df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'date', 'sector_code', 'sector_name', 'sector_type',
                    'main_net_inflow', 'pct_change', 'leading_stock', 'leading_stock_pct'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            # Note: akshare sector fund flow doesn't have date column, use today's date
            from datetime import datetime
            standardized['date'] = datetime.now().strftime('%Y-%m-%d')
            standardized['sector_code'] = raw_df.index.astype(str)  # No sector code column, use index
            standardized['sector_name'] = raw_df['名称'].astype(str)
            standardized['sector_type'] = sector_type
            # API returns '今日主力净流入-净额' instead of '主力净流入-净额'
            standardized['main_net_inflow'] = pd.to_numeric(raw_df['今日主力净流入-净额'], errors='coerce')
            standardized['pct_change'] = pd.to_numeric(raw_df['今日涨跌幅'], errors='coerce')
            standardized['leading_stock'] = raw_df.get('今日主力净流入最大股', pd.Series([''] * len(raw_df))).astype(str)
            standardized['leading_stock_pct'] = 0.0  # Not provided in new API
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch sector fund flow data: {e}") from e
    
    def get_main_fund_flow_rank(
        self,
        date: str,
        indicator: str
    ) -> pd.DataFrame:
        """
        Get main fund flow ranking from Eastmoney.
        
        Args:
            date: Date (YYYY-MM-DD)
            indicator: Ranking indicator ('net_inflow' or 'net_inflow_rate')
        
        Returns:
            pd.DataFrame: Ranked fund flow data
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date(date)
        if indicator not in ['net_inflow', 'net_inflow_rate']:
            raise ValueError(
                f"Invalid indicator: {indicator}. "
                "Must be 'net_inflow' or 'net_inflow_rate'"
            )
        
        try:
            import akshare as ak
            
            # Map indicator to akshare parameter
            indicator_map = {
                'net_inflow': '今日',
                'net_inflow_rate': '今日'
            }
            
            # Call akshare function
            raw_df = ak.stock_individual_fund_flow_rank(indicator=indicator_map[indicator])
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'rank', 'symbol', 'name', 'main_net_inflow', 'pct_change'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['rank'] = range(1, len(raw_df) + 1)
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['名称'].astype(str)
            # API returns '今日主力净流入-净额' instead of '主力净流入-净额'
            standardized['main_net_inflow'] = pd.to_numeric(raw_df['今日主力净流入-净额'], errors='coerce')
            standardized['pct_change'] = pd.to_numeric(raw_df['今日涨跌幅'], errors='coerce')
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch main fund flow rank: {e}") from e
    
    def get_industry_list(self) -> pd.DataFrame:
        """
        Get list of industry sectors from Eastmoney.
        
        Returns:
            pd.DataFrame: Industry sector list with columns:
                - sector_code: Sector code
                - sector_name: Sector name
                - constituent_count: Number of constituent stocks
        """
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.stock_board_industry_name_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'sector_code', 'sector_name', 'constituent_count'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['sector_code'] = raw_df['板块代码'].astype(str)
            standardized['sector_name'] = raw_df['板块名称'].astype(str)
            standardized['constituent_count'] = pd.to_numeric(raw_df.get('公司数量', pd.Series([0] * len(raw_df))), errors='coerce').astype(int)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch industry list: {e}") from e
    
    def get_industry_constituents(self, industry_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of an industry sector from Eastmoney.
        
        Args:
            industry_code: Industry sector code
        
        Returns:
            pd.DataFrame: Constituent stocks with columns:
                - symbol: Stock symbol
                - name: Stock name
                - weight: Weight in the sector
        
        Raises:
            ValueError: If industry_code is invalid
        """
        if not industry_code:
            raise ValueError("industry_code cannot be empty")
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.stock_board_industry_cons_em(symbol=industry_code)
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'symbol', 'name', 'weight'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['名称'].astype(str)
            # Weight is not provided by akshare, set to None
            standardized['weight'] = None
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch industry constituents: {e}") from e
    
    def get_concept_list(self) -> pd.DataFrame:
        """
        Get list of concept sectors from Eastmoney.
        
        Returns:
            pd.DataFrame: Concept sector list with columns:
                - sector_code: Sector code
                - sector_name: Sector name
                - constituent_count: Number of constituent stocks
        """
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.stock_board_concept_name_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'sector_code', 'sector_name', 'constituent_count'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['sector_code'] = raw_df['板块代码'].astype(str)
            standardized['sector_name'] = raw_df['板块名称'].astype(str)
            standardized['constituent_count'] = pd.to_numeric(raw_df.get('公司数量', pd.Series([0] * len(raw_df))), errors='coerce').astype(int)
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch concept list: {e}") from e
    
    def get_concept_constituents(self, concept_code: str) -> pd.DataFrame:
        """
        Get constituent stocks of a concept sector from Eastmoney.
        
        Args:
            concept_code: Concept sector code
        
        Returns:
            pd.DataFrame: Constituent stocks with columns:
                - symbol: Stock symbol
                - name: Stock name
                - weight: Weight in the sector
        
        Raises:
            ValueError: If concept_code is invalid
        """
        if not concept_code:
            raise ValueError("concept_code cannot be empty")
        
        try:
            import akshare as ak
            
            # Call akshare function
            raw_df = ak.stock_board_concept_cons_em(symbol=concept_code)
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'symbol', 'name', 'weight'
                ])
            
            # Standardize the data
            standardized = pd.DataFrame()
            standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['名称'].astype(str)
            # Weight is not provided by akshare, set to None
            standardized['weight'] = None
            
            # Ensure JSON compatibility
            return self.ensure_json_compatible(standardized)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch concept constituents: {e}") from e
