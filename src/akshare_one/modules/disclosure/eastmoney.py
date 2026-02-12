"""
Eastmoney disclosure news data provider.

This module implements the disclosure news data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from .base import DisclosureProvider


class EastmoneyDisclosureProvider(DisclosureProvider):
    """
    Disclosure news data provider using Eastmoney as the data source.
    
    This provider wraps akshare functions to fetch disclosure news data from Eastmoney
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
    
    def get_disclosure_news(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        category: str
    ) -> pd.DataFrame:
        """
        Get disclosure news data from Eastmoney.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')
        
        Returns:
            pd.DataFrame: Standardized disclosure news data with columns:
                - date: Announcement date (YYYY-MM-DD)
                - symbol: Stock symbol
                - title: Announcement title
                - category: Announcement category
                - content: Announcement summary
                - url: Announcement URL
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        if category not in ['all', 'dividend', 'repurchase', 'st', 'major_event']:
            raise ValueError(
                f"Invalid category: {category}. "
                "Must be one of: 'all', 'dividend', 'repurchase', 'st', 'major_event'"
            )
        
        # Fetch data from akshare
        try:
            import akshare as ak
            from datetime import datetime, timedelta
            
            # Convert dates to datetime objects
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Collect data for each date in the range
            # Note: akshare's stock_notice_report only supports single date queries
            all_data = []
            current_dt = start_dt
            
            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y%m%d')
                try:
                    # Fetch data for this date
                    df = ak.stock_notice_report(symbol="全部", date=date_str)
                    if not df.empty:
                        all_data.append(df)
                except Exception:
                    # Skip dates with no data or errors
                    pass
                
                # Move to next day
                current_dt += timedelta(days=1)
            
            # Combine all data
            if not all_data:
                return self.create_empty_dataframe([
                    'date', 'symbol', 'title', 'category', 'content', 'url'
                ])
            
            raw_df = pd.concat(all_data, ignore_index=True)
            
            # Standardize the data
            return self._standardize_disclosure_news(raw_df, symbol, category)
            
        except Exception:
            # Return empty DataFrame on error
            return self.create_empty_dataframe([
                'date', 'symbol', 'title', 'category', 'content', 'url'
            ])
    
    def _standardize_disclosure_news(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None,
        category_filter: str
    ) -> pd.DataFrame:
        """
        Standardize disclosure news data.
        
        Args:
            raw_df: Raw data from akshare
            symbol_filter: Stock symbol to filter (or None for all)
            category_filter: Category to filter
        
        Returns:
            pd.DataFrame: Standardized disclosure news data
        """
        if raw_df.empty:
            return self.create_empty_dataframe([
                'date', 'symbol', 'title', 'category', 'content', 'url'
            ])
        
        # Create standardized DataFrame
        standardized = pd.DataFrame()
        
        # Map fields
        standardized['date'] = pd.to_datetime(raw_df['公告日期']).dt.strftime('%Y-%m-%d')
        standardized['symbol'] = raw_df['代码'].astype(str).str.zfill(6)
        standardized['title'] = raw_df['公告标题'].astype(str)
        standardized['category'] = raw_df['公告类型'].astype(str)
        standardized['content'] = ''  # Not available in this data source
        standardized['url'] = raw_df['网址'].astype(str)
        
        # Filter by symbol if specified
        if symbol_filter:
            standardized = standardized[standardized['symbol'] == symbol_filter.zfill(6)]
        
        # Filter by category if not 'all'
        if category_filter != 'all':
            standardized = self._filter_by_category(standardized, category_filter)
        
        # Ensure JSON compatibility
        standardized = self.ensure_json_compatible(standardized)
        
        # Sort by date descending
        standardized = standardized.sort_values('date', ascending=False).reset_index(drop=True)
        
        return standardized
    
    def _filter_by_category(self, df: pd.DataFrame, category: str) -> pd.DataFrame:
        """
        Filter disclosure news by category.
        
        Args:
            df: Standardized DataFrame
            category: Category to filter ('dividend', 'repurchase', 'st', 'major_event')
        
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df
        
        # Define category keywords mapping
        category_keywords = {
            'dividend': ['分红', '派息', '红利', '股息', '现金分红'],
            'repurchase': ['回购', '股份回购', '回购股份'],
            'st': ['ST', '*ST', 'SST', '退市', '风险警示', '风险提示'],
            'major_event': ['重大事项', '重大合同', '重大资产', '重组', '收购', '兼并']
        }
        
        keywords = category_keywords.get(category, [])
        if not keywords:
            return df
        
        # Filter by keywords in title or category
        mask = df['title'].str.contains('|'.join(keywords), case=False, na=False) | \
               df['category'].str.contains('|'.join(keywords), case=False, na=False)
        
        return df[mask].reset_index(drop=True)
    
    def get_dividend_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get dividend data from Eastmoney.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized dividend data with columns:
                - symbol: Stock symbol
                - fiscal_year: Dividend fiscal year
                - dividend_per_share: Dividend per share
                - record_date: Record date (YYYY-MM-DD)
                - ex_dividend_date: Ex-dividend date (YYYY-MM-DD)
                - payment_date: Payment date (YYYY-MM-DD)
                - dividend_ratio: Dividend ratio
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        
        # Fetch data from akshare
        try:
            import akshare as ak
            from datetime import datetime
            
            if symbol:
                # Fetch data for single stock
                raw_df = ak.stock_dividend_cninfo(symbol=symbol)
                if raw_df.empty:
                    return self.create_empty_dataframe([
                        'symbol', 'fiscal_year', 'dividend_per_share',
                        'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
                    ])
                
                # Standardize the data
                return self._standardize_dividend_data(raw_df, symbol, start_date, end_date)
            else:
                # For all stocks, we would need to iterate through all symbols
                # This is not practical, so return empty DataFrame
                # In production, this would require a different data source or approach
                return self.create_empty_dataframe([
                    'symbol', 'fiscal_year', 'dividend_per_share',
                    'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
                ])
                
        except Exception:
            # Return empty DataFrame on error
            return self.create_empty_dataframe([
                'symbol', 'fiscal_year', 'dividend_per_share',
                'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
            ])
    
    def _standardize_dividend_data(
        self,
        raw_df: pd.DataFrame,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Standardize dividend data.
        
        Args:
            raw_df: Raw data from akshare
            symbol: Stock symbol
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            pd.DataFrame: Standardized dividend data
        """
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'fiscal_year', 'dividend_per_share',
                'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
            ])
        
        # Create standardized DataFrame
        standardized = pd.DataFrame()
        
        # Add symbol (repeat for each row)
        standardized['symbol'] = [symbol.zfill(6)] * len(raw_df)
        
        # Extract fiscal year from report time
        standardized['fiscal_year'] = raw_df['报告时间'].astype(str)
        
        # Calculate dividend per share from 派息比例 (e.g., "10派1.5元" means 0.15 per share)
        standardized['dividend_per_share'] = raw_df['派息比例'].apply(
            lambda x: float(x) / 10.0 if pd.notna(x) and x != 0 else None
        )
        
        # Convert dates to standard format
        standardized['record_date'] = pd.to_datetime(
            raw_df['股权登记日'], errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        
        standardized['ex_dividend_date'] = pd.to_datetime(
            raw_df['除权日'], errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        
        standardized['payment_date'] = pd.to_datetime(
            raw_df['派息日'], errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        
        # Dividend ratio is not available in source data, set to None
        standardized['dividend_ratio'] = None
        
        # Filter by date range (using ex_dividend_date as the reference)
        if start_date or end_date:
            # Convert to datetime for comparison
            ex_dates = pd.to_datetime(raw_df['除权日'], errors='coerce')
            start_dt = pd.to_datetime(start_date) if start_date else pd.Timestamp.min
            end_dt = pd.to_datetime(end_date) if end_date else pd.Timestamp.max
            
            mask = (ex_dates >= start_dt) & (ex_dates <= end_dt)
            standardized = standardized[mask]
        
        # Ensure JSON compatibility
        standardized = self.ensure_json_compatible(standardized)
        
        # Sort by ex_dividend_date descending
        standardized = standardized.sort_values(
            'ex_dividend_date', ascending=False, na_position='last'
        ).reset_index(drop=True)
        
        return standardized
    
    def get_repurchase_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get stock repurchase data from Eastmoney.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized repurchase data with columns:
                - symbol: Stock symbol
                - announcement_date: Announcement date (YYYY-MM-DD)
                - progress: Repurchase progress
                - amount: Repurchase amount
                - quantity: Repurchase quantity
                - price_range: Repurchase price range
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        
        # Fetch data from akshare
        try:
            import akshare as ak
            from datetime import datetime
            
            # Fetch all repurchase data
            raw_df = ak.stock_repurchase_em()
            
            if raw_df.empty:
                return self.create_empty_dataframe([
                    'symbol', 'announcement_date', 'progress',
                    'amount', 'quantity', 'price_range'
                ])
            
            # Standardize the data
            return self._standardize_repurchase_data(raw_df, symbol, start_date, end_date)
                
        except Exception:
            # Return empty DataFrame on error
            return self.create_empty_dataframe([
                'symbol', 'announcement_date', 'progress',
                'amount', 'quantity', 'price_range'
            ])
    
    def _standardize_repurchase_data(
        self,
        raw_df: pd.DataFrame,
        symbol_filter: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Standardize repurchase data.
        
        Args:
            raw_df: Raw data from akshare
            symbol_filter: Stock symbol to filter (or None for all)
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            pd.DataFrame: Standardized repurchase data
        """
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'announcement_date', 'progress',
                'amount', 'quantity', 'price_range'
            ])
        
        # Create standardized DataFrame
        standardized = pd.DataFrame()
        
        # Map fields
        standardized['symbol'] = raw_df['股票代码'].astype(str).str.zfill(6)
        
        # Convert announcement date
        standardized['announcement_date'] = pd.to_datetime(
            raw_df['最新公告日期'], errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        
        # Progress status
        standardized['progress'] = raw_df['实施进度'].astype(str)
        
        # Amount (use 已回购金额 if available, otherwise use 计划回购金额区间-下限)
        standardized['amount'] = raw_df['已回购金额'].fillna(
            raw_df['计划回购金额区间-下限']
        )
        
        # Quantity (use 已回购股份数量 if available)
        standardized['quantity'] = raw_df['已回购股份数量']
        
        # Price range (combine lower and upper bounds)
        price_lower = raw_df['计划回购价格区间'].astype(str)
        standardized['price_range'] = price_lower
        
        # Filter by symbol if specified
        if symbol_filter:
            standardized = standardized[
                standardized['symbol'] == symbol_filter.zfill(6)
            ]
        
        # Filter by date range
        if start_date or end_date:
            dates = pd.to_datetime(raw_df['最新公告日期'], errors='coerce')
            start_dt = pd.to_datetime(start_date) if start_date else pd.Timestamp.min
            end_dt = pd.to_datetime(end_date) if end_date else pd.Timestamp.max
            
            mask = (dates >= start_dt) & (dates <= end_dt)
            standardized = standardized[mask]
        
        # Ensure JSON compatibility
        standardized = self.ensure_json_compatible(standardized)
        
        # Sort by announcement_date descending
        standardized = standardized.sort_values(
            'announcement_date', ascending=False, na_position='last'
        ).reset_index(drop=True)
        
        return standardized
    
    def get_st_delist_data(self, symbol: str | None) -> pd.DataFrame:
        """
        Get ST/delist risk data from Eastmoney.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
        
        Returns:
            pd.DataFrame: Standardized ST/delist risk data with columns:
                - symbol: Stock symbol
                - name: Stock name
                - st_type: ST type
                - risk_level: Risk level
                - announcement_date: Announcement date (YYYY-MM-DD)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if symbol:
            self.validate_symbol(symbol)
        
        # Fetch data from akshare
        try:
            import akshare as ak
            
            # Fetch delist data from both SH and SZ exchanges
            sh_df = ak.stock_info_sh_delist()
            sz_df = ak.stock_info_sz_delist()
            
            # Combine the data
            all_data = []
            
            if not sh_df.empty:
                all_data.append(self._standardize_delist_data(sh_df, 'sh'))
            
            if not sz_df.empty:
                all_data.append(self._standardize_delist_data(sz_df, 'sz'))
            
            if not all_data:
                return self.create_empty_dataframe([
                    'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
                ])
            
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Filter by symbol if specified
            if symbol:
                combined_df = combined_df[
                    combined_df['symbol'] == symbol.zfill(6)
                ]
            
            # Ensure JSON compatibility
            combined_df = self.ensure_json_compatible(combined_df)
            
            return combined_df
                
        except Exception:
            # Return empty DataFrame on error
            return self.create_empty_dataframe([
                'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
            ])
    
    def _standardize_delist_data(
        self,
        raw_df: pd.DataFrame,
        market: str
    ) -> pd.DataFrame:
        """
        Standardize delist data from SH or SZ exchange.
        
        Args:
            raw_df: Raw data from akshare
            market: Market identifier ('sh' or 'sz')
        
        Returns:
            pd.DataFrame: Standardized delist data
        """
        if raw_df.empty:
            return self.create_empty_dataframe([
                'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
            ])
        
        # Create standardized DataFrame
        standardized = pd.DataFrame()
        
        # Map fields based on market
        if market == 'sh':
            standardized['symbol'] = raw_df['公司代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['公司简称'].astype(str)
            date_col = '暂停上市日期'
        else:  # sz
            standardized['symbol'] = raw_df['证券代码'].astype(str).str.zfill(6)
            standardized['name'] = raw_df['证券简称'].astype(str)
            date_col = '终止上市日期'
        
        # Determine ST type from name
        standardized['st_type'] = standardized['name'].apply(
            lambda x: self.standardize_st_type(x)
        )
        
        # Determine risk level from name (not ST type, as name contains more info)
        standardized['risk_level'] = standardized['name'].apply(
            lambda x: self.standardize_risk_level(x)
        )
        
        # Convert announcement date
        standardized['announcement_date'] = pd.to_datetime(
            raw_df[date_col], errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        
        return standardized
