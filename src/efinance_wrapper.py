"""
Efinance library wrapper module
Provides unified interface to efinance stock, fund, bond, and futures data
"""

import efinance as ef
from typing import Union, List, Optional, Dict
import pandas as pd


class StockAPI:
    """Stock market data interface"""

    @staticmethod
    def get_quote_history(
        stock_codes: Union[str, List[str]],
        beg: str = "19000101",
        end: str = "20500101",
        klt: int = 101,
        fqt: int = 1,
        **kwargs,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Get stock historical K-line data

        Args:
            stock_codes: Stock code or list of codes
            beg: Start date (YYYYMMDD)
            end: End date (YYYYMMDD)
            klt: Frequency (101=daily, 102=weekly, 103=monthly, 5=5min, etc.)
            fqt: Adjustment type (0=none, 1=forward, 2=backward)

        Returns:
            DataFrame or Dict of DataFrames
        """
        return ef.stock.get_quote_history(stock_codes, beg=beg, end=end, klt=klt, fqt=fqt, **kwargs)

    @staticmethod
    def get_realtime_quotes(fs: Union[str, List[str]] = None, **kwargs) -> pd.DataFrame:
        """
        Get real-time stock quotes

        Args:
            fs: Filter string or list

        Returns:
            DataFrame with real-time quotes
        """
        return ef.stock.get_realtime_quotes(fs=fs, **kwargs)

    @staticmethod
    def get_base_info(stock_codes: Union[str, List[str]]) -> Union[pd.Series, pd.DataFrame]:
        """
        Get stock basic information

        Args:
            stock_codes: Stock code or list of codes

        Returns:
            Series or DataFrame with basic info
        """
        return ef.stock.get_base_info(stock_codes)

    @staticmethod
    def get_daily_billboard(start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get dragon-tiger list data

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with dragon-tiger list
        """
        return ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)

    @staticmethod
    def get_all_company_performance(date: str = None) -> pd.DataFrame:
        """
        Get all company quarterly performance

        Args:
            date: Report date

        Returns:
            DataFrame with performance data
        """
        return ef.stock.get_all_company_performance(date=date)

    @staticmethod
    def get_history_bill(stock_code: str) -> pd.DataFrame:
        """
        Get historical fund flow data

        Args:
            stock_code: Stock code

        Returns:
            DataFrame with historical fund flow
        """
        return ef.stock.get_history_bill(stock_code)

    @staticmethod
    def get_today_bill(stock_code: str) -> pd.DataFrame:
        """
        Get today's fund flow data

        Args:
            stock_code: Stock code

        Returns:
            DataFrame with today's fund flow
        """
        return ef.stock.get_today_bill(stock_code)

    @staticmethod
    def get_deal_detail(stock_code: str, max_count: int = 1000000, **kwargs) -> pd.DataFrame:
        """
        Get transaction details

        Args:
            stock_code: Stock code
            max_count: Maximum count

        Returns:
            DataFrame with transaction details
        """
        return ef.stock.get_deal_detail(stock_code, max_count=max_count, **kwargs)

    @staticmethod
    def get_top10_stock_holder_info(stock_code: str, top: int = 4) -> pd.DataFrame:
        """
        Get top 10 shareholders info

        Args:
            stock_code: Stock code
            top: Top N periods

        Returns:
            DataFrame with shareholders info
        """
        return ef.stock.get_top10_stock_holder_info(stock_code, top=top)

    @staticmethod
    def get_belong_board(stock_code: str) -> pd.DataFrame:
        """
        Get board membership

        Args:
            stock_code: Stock code

        Returns:
            DataFrame with board info
        """
        return ef.stock.get_belong_board(stock_code)

    @staticmethod
    def get_members(index_code: str) -> pd.DataFrame:
        """
        Get index members

        Args:
            index_code: Index code

        Returns:
            DataFrame with index members
        """
        return ef.stock.get_members(index_code)

    @staticmethod
    def get_quote_snapshot(stock_code: str) -> pd.Series:
        """
        Get quote snapshot

        Args:
            stock_code: Stock code

        Returns:
            Series with quote snapshot
        """
        return ef.stock.get_quote_snapshot(stock_code)

    @staticmethod
    def get_latest_quote(stock_codes: Union[str, List[str]], **kwargs) -> pd.DataFrame:
        """
        Get latest quote

        Args:
            stock_codes: Stock code or list

        Returns:
            DataFrame with latest quotes
        """
        return ef.stock.get_latest_quote(stock_codes, **kwargs)

    @staticmethod
    def get_latest_ipo_info() -> pd.DataFrame:
        """
        Get latest IPO info

        Returns:
            DataFrame with IPO info
        """
        return ef.stock.get_latest_ipo_info()

    @staticmethod
    def get_latest_holder_number(date: str = None) -> pd.DataFrame:
        """
        Get latest holder number

        Args:
            date: Date string

        Returns:
            DataFrame with holder numbers
        """
        return ef.stock.get_latest_holder_number(date=date)

    @staticmethod
    def get_all_report_dates() -> pd.DataFrame:
        """
        Get all report dates

        Returns:
            DataFrame with report dates
        """
        return ef.stock.get_all_report_dates()


class FundAPI:
    """Fund data interface"""

    @staticmethod
    def get_quote_history(fund_code: str, pz: int = 40000) -> pd.DataFrame:
        """
        Get fund historical net value

        Args:
            fund_code: Fund code
            pz: Page size

        Returns:
            DataFrame with historical net value
        """
        return ef.fund.get_quote_history(fund_code, pz=pz)

    @staticmethod
    def get_quote_history_multi(fund_codes: List[str], pz: int = 40000, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Get multiple funds historical data

        Args:
            fund_codes: List of fund codes
            pz: Page size

        Returns:
            Dict of DataFrames
        """
        return ef.fund.get_quote_history_multi(fund_codes, pz=pz, **kwargs)

    @staticmethod
    def get_base_info(fund_codes: Union[str, List[str]]) -> Union[pd.Series, pd.DataFrame]:
        """
        Get fund basic information

        Args:
            fund_codes: Fund code or list

        Returns:
            Series or DataFrame with basic info
        """
        return ef.fund.get_base_info(fund_codes)

    @staticmethod
    def get_invest_position(fund_code: str, dates: Union[str, List[str]] = None) -> pd.DataFrame:
        """
        Get fund holdings position

        Args:
            fund_code: Fund code
            dates: Date or list of dates

        Returns:
            DataFrame with holdings
        """
        return ef.fund.get_invest_position(fund_code, dates=dates)

    @staticmethod
    def get_fund_codes(ft: str = None) -> pd.DataFrame:
        """
        Get all fund codes

        Args:
            ft: Fund type

        Returns:
            DataFrame with fund codes
        """
        return ef.fund.get_fund_codes(ft=ft)

    @staticmethod
    def get_fund_manager(ft: str) -> pd.DataFrame:
        """
        Get fund manager info

        Args:
            ft: Fund type

        Returns:
            DataFrame with manager info
        """
        return ef.fund.get_fund_manager(ft)

    @staticmethod
    def get_industry_distribution(fund_code: str, dates: Union[str, List[str]] = None) -> pd.DataFrame:
        """
        Get fund industry distribution

        Args:
            fund_code: Fund code
            dates: Date or list

        Returns:
            DataFrame with industry distribution
        """
        return ef.fund.get_industry_distribution(fund_code, dates=dates)

    @staticmethod
    def get_types_percentage(fund_code: str, dates: Union[List[str], str, None] = None) -> pd.DataFrame:
        """
        Get fund asset allocation

        Args:
            fund_code: Fund code
            dates: Date or list

        Returns:
            DataFrame with asset allocation
        """
        return ef.fund.get_types_percentage(fund_code, dates=dates)

    @staticmethod
    def get_period_change(fund_code: str) -> pd.DataFrame:
        """
        Get fund period changes

        Args:
            fund_code: Fund code

        Returns:
            DataFrame with period changes
        """
        return ef.fund.get_period_change(fund_code)

    @staticmethod
    def get_public_dates(fund_code: str) -> List[str]:
        """
        Get fund public dates

        Args:
            fund_code: Fund code

        Returns:
            List of dates
        """
        return ef.fund.get_public_dates(fund_code)

    @staticmethod
    def get_realtime_increase_rate(fund_codes: Union[List[str], str]) -> pd.DataFrame:
        """
        Get realtime increase rate

        Args:
            fund_codes: Fund code or list

        Returns:
            DataFrame with increase rates
        """
        return ef.fund.get_realtime_increase_rate(fund_codes)

    @staticmethod
    def get_pdf_reports(fund_code: str, max_count: int = 12, save_dir: str = "pdf") -> None:
        """
        Download fund PDF reports

        Args:
            fund_code: Fund code
            max_count: Maximum count
            save_dir: Save directory
        """
        return ef.fund.get_pdf_reports(fund_code, max_count=max_count, save_dir=save_dir)


class BondAPI:
    """Bond data interface"""

    @staticmethod
    def get_quote_history(
        bond_codes: Union[str, List[str]],
        beg: str = "19000101",
        end: str = "20500101",
        klt: int = 101,
        fqt: int = 1,
        **kwargs,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Get bond historical K-line

        Args:
            bond_codes: Bond code or list
            beg: Start date
            end: End date
            klt: Frequency
            fqt: Adjustment type

        Returns:
            DataFrame or Dict of DataFrames
        """
        return ef.bond.get_quote_history(bond_codes, beg=beg, end=end, klt=klt, fqt=fqt, **kwargs)

    @staticmethod
    def get_realtime_quotes(**kwargs) -> pd.DataFrame:
        """
        Get realtime bond quotes

        Returns:
            DataFrame with realtime quotes
        """
        return ef.bond.get_realtime_quotes(**kwargs)

    @staticmethod
    def get_all_base_info() -> pd.DataFrame:
        """
        Get all bonds basic info

        Returns:
            DataFrame with all bonds info
        """
        return ef.bond.get_all_base_info()

    @staticmethod
    def get_base_info(bond_codes: Union[str, List[str]]) -> Union[pd.DataFrame, pd.Series]:
        """
        Get bond basic info

        Args:
            bond_codes: Bond code or list

        Returns:
            DataFrame or Series with basic info
        """
        return ef.bond.get_base_info(bond_codes)

    @staticmethod
    def get_deal_detail(bond_code: str, max_count: int = 1000000, **kwargs) -> pd.DataFrame:
        """
        Get bond transaction details

        Args:
            bond_code: Bond code
            max_count: Maximum count

        Returns:
            DataFrame with transaction details
        """
        return ef.bond.get_deal_detail(bond_code, max_count=max_count, **kwargs)

    @staticmethod
    def get_history_bill(bond_code: str) -> pd.DataFrame:
        """
        Get historical fund flow

        Args:
            bond_code: Bond code

        Returns:
            DataFrame with historical flow
        """
        return ef.bond.get_history_bill(bond_code)

    @staticmethod
    def get_today_bill(bond_code: str) -> pd.DataFrame:
        """
        Get today's fund flow

        Args:
            bond_code: Bond code

        Returns:
            DataFrame with today's flow
        """
        return ef.bond.get_today_bill(bond_code)


class FuturesAPI:
    """Futures data interface"""

    @staticmethod
    def get_quote_history(
        quote_ids: Union[str, List[str]],
        beg: str = "19000101",
        end: str = "20500101",
        klt: int = 101,
        fqt: int = 1,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get futures historical K-line

        Args:
            quote_ids: Quote ID or list
            beg: Start date
            end: End date
            klt: Frequency
            fqt: Adjustment type

        Returns:
            DataFrame with historical data
        """
        return ef.futures.get_quote_history(quote_ids, beg=beg, end=end, klt=klt, fqt=fqt, **kwargs)

    @staticmethod
    def get_realtime_quotes() -> pd.DataFrame:
        """
        Get realtime futures quotes

        Returns:
            DataFrame with realtime quotes
        """
        return ef.futures.get_realtime_quotes()

    @staticmethod
    def get_futures_base_info() -> pd.DataFrame:
        """
        Get futures basic info

        Returns:
            DataFrame with futures info
        """
        return ef.futures.get_futures_base_info()

    @staticmethod
    def get_deal_detail(quote_id: str, max_count: int = 1000000) -> pd.DataFrame:
        """
        Get futures transaction details

        Args:
            quote_id: Quote ID
            max_count: Maximum count

        Returns:
            DataFrame with transaction details
        """
        return ef.futures.get_deal_detail(quote_id, max_count=max_count)


class EfinanceWrapper:
    """
    Efinance unified wrapper
    Provides access to all efinance APIs
    """

    stock = StockAPI
    fund = FundAPI
    bond = BondAPI
    futures = FuturesAPI

    def __init__(self):
        pass


efinance_api = EfinanceWrapper()
