import time
import warnings

import pandas as pd

from ......logging_config import get_logger, log_api_request
from .....core.cache import cache
from .base import DividendDataFactory, DividendDataProvider

warnings.filterwarnings("ignore", message=".*lzma.*")


@DividendDataFactory.register("baostock")
class BaostockDividendProvider(DividendDataProvider):
    _bs_instance = None
    _is_logged_in = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        self._ensure_login()

    @classmethod
    def _ensure_login(cls):
        if not cls._is_logged_in:
            try:
                import baostock as bs

                cls._bs_instance = bs
                lg = bs.login()
                if lg.error_code == "0":
                    cls._is_logged_in = True
                else:
                    raise ConnectionError(f"Baostock login failed: {lg.error_msg}")
            except ImportError:
                raise ImportError("baostock is not installed. Install it with: pip install baostock")

    @classmethod
    def logout(cls):
        if cls._is_logged_in and cls._bs_instance:
            cls._bs_instance.logout()
            cls._is_logged_in = False

    @cache(
        "dividend_data_cache",
        key=lambda self, **kwargs: f"baostock_dividend_{self.symbol}_{self.start_date}_{self.end_date}",
    )
    def get_dividend_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching dividend data",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": self.symbol,
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                        "action": "fetch_start",
                    }
                },
            )

            df = self._query_dividend_data()

            df = self.standardize_and_filter(df, "baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="dividend",
                params={"symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="dividend",
                params={"symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch dividend data: {str(e)}") from e

    @cache(
        "adjust_factor_cache",
        key=lambda self, **kwargs: f"baostock_adjust_factor_{self.symbol}_{self.start_date}_{self.end_date}",
    )
    def get_adjust_factor(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching adjust factor data",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": self.symbol,
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                        "action": "fetch_start",
                    }
                },
            )

            df = self._query_adjust_factor()

            df = self.standardize_and_filter(df, "baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="adjust_factor",
                params={"symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="adjust_factor",
                params={"symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch adjust factor data: {str(e)}") from e

    def _query_dividend_data(self) -> pd.DataFrame:
        bs_code = self._convert_symbol_to_baostock_format(self.symbol)

        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        rs = self._bs_instance.query_dividend_data(
            code=bs_code,
            start_date=start_date,
            end_date=end_date,
        )

        if rs.error_code != "0":
            raise ValueError(f"Baostock query dividend failed: {rs.error_msg}")

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        raw_df = pd.DataFrame(data_list, columns=rs.fields)

        return self._clean_dividend_data(raw_df)

    def _query_adjust_factor(self) -> pd.DataFrame:
        bs_code = self._convert_symbol_to_baostock_format(self.symbol)

        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        rs = self._bs_instance.query_adjust_factor(
            code=bs_code,
            start_date=start_date,
            end_date=end_date,
        )

        if rs.error_code != "0":
            raise ValueError(f"Baostock query adjust factor failed: {rs.error_msg}")

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        raw_df = pd.DataFrame(data_list, columns=rs.fields)

        return self._clean_adjust_factor_data(raw_df)

    def _convert_symbol_to_baostock_format(self, symbol: str) -> str:
        if symbol.startswith(("sh.", "sz.", "bj.")):
            return symbol

        if len(symbol) != 6:
            raise ValueError(f"Invalid symbol format: {symbol}")

        if symbol.startswith(("6", "9")):
            return f"sh.{symbol}"
        elif symbol.startswith(("0", "3", "2")):
            return f"sz.{symbol}"
        else:
            raise ValueError(f"Unknown market for symbol: {symbol}")

    def _convert_date_format(self, date_str: str) -> str:
        return date_str

    def _clean_dividend_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        column_map = {
            "code": "symbol",
            "divDate": "div_date",
            "divYear": "div_year",
            "divReportDate": "div_report_date",
            "divAccountDate": "div_account_date",
            "divPayDate": "div_pay_date",
            "divAnnDate": "div_ann_date",
            "cashPay": "cash_dividend",
            "bonusType": "bonus_type",
            "bonusAmtRation": "bonus_amt_ratio",
            "transferAmtRation": "transfer_amt_ratio",
            "bonusShareRation": "bonus_share_ratio",
            "transferShareRation": "transfer_share_ratio",
            "allotShareRation": "allot_share_ratio",
            "allotPrice": "allot_price",
            "recordDate": "record_date",
            "exRightDate": "ex_right_date",
            "exDivDate": "ex_div_date",
            "pubDate": "pub_date",
        }

        available_columns = {src: target for src, target in column_map.items() if src in raw_df.columns}

        if not available_columns:
            return raw_df

        df = raw_df.rename(columns=available_columns)

        numeric_columns = [
            "cash_dividend",
            "bonus_amt_ratio",
            "transfer_amt_ratio",
            "bonus_share_ratio",
            "transfer_share_ratio",
            "allot_share_ratio",
            "allot_price",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        date_columns = [
            "div_date",
            "div_report_date",
            "div_account_date",
            "div_pay_date",
            "div_ann_date",
            "record_date",
            "ex_right_date",
            "ex_div_date",
            "pub_date",
        ]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].str.replace(r"^(sh\.|sz\.)", "", regex=True)

        return df

    def _clean_adjust_factor_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        column_map = {
            "code": "symbol",
            "date": "date",
            "foreAdjustFactor": "fore_adjust_factor",
            "backAdjustFactor": "back_adjust_factor",
            "adjustFactor": "adjust_factor",
        }

        available_columns = {src: target for src, target in column_map.items() if src in raw_df.columns}

        if not available_columns:
            return raw_df

        df = raw_df.rename(columns=available_columns)

        numeric_columns = ["fore_adjust_factor", "back_adjust_factor", "adjust_factor"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].str.replace(r"^(sh\.|sz\.)", "", regex=True)

        return df
