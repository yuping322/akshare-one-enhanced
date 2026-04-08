"""
Efinance futures data provider.

This module implements futures data provider using efinance as the data source.
"""

import pandas as pd

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False
    ef = None

from ..cache import cache
from .base import (
    FuturesHistoricalFactory,
    FuturesRealtimeFactory,
    HistoricalFuturesDataProvider,
    RealtimeFuturesDataProvider,
)


_EXCHANGE_CODE_MAP = {
    "SHFE": "1",  # 上海期货交易所
    "DCE": "2",  # 大连商品交易所
    "ZCE": "3",  # 郑州商品交易所 (CZCE in some contexts)
    "CZCE": "3",  # 郑州商品交易所
    "CFFEX": "4",  # 中国金融期货交易所
    "INE": "5",  # 上海国际能源交易中心
}

_EXCHANGE_NAME_MAP = {
    "1": "SHFE",
    "2": "DCE",
    "3": "CZCE",
    "4": "CFFEX",
    "5": "INE",
}


@FuturesHistoricalFactory.register("efinance")
class EfinanceFuturesHistoricalProvider(HistoricalFuturesDataProvider):
    """Adapter for efinance futures historical data API"""

    _API_MAP = {
        "get_hist_data": {
            "ak_func": None,  # Direct efinance API call
        },
        "get_main_contracts": {
            "ak_func": None,  # Direct efinance API call
        },
    }

    def get_source_name(self) -> str:
        return "efinance"

    @cache(
        "futures_hist_cache",
        key=lambda self: (
            f"efinance_futures_hist_{self.symbol}_{self.contract}_{self.interval}_{self.interval_multiplier}"
        ),
    )
    def get_hist_data(self) -> pd.DataFrame:
        """Fetches efinance historical futures market data

        Returns:
            pd.DataFrame:
            - timestamp: 时间戳
            - symbol: 期货代码
            - contract: 合约代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - open_interest: 持仓量
            - settlement: 结算价
        """
        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance library is not installed. Please install it with: pip install efinance")

        self.interval = self.interval.lower()
        self._validate_interval_params(self.interval, self.interval_multiplier)

        try:
            quote_id = self._get_quote_id()

            beg = self._convert_date_format(self.start_date)
            end = self._convert_date_format(self.end_date)

            klt = self._get_klt_parameter()

            raw_df = ef.futures.get_quote_history(quote_id, beg=beg, end=end, klt=klt)

            if raw_df is None or raw_df.empty:
                raise ValueError(f"No historical data found for futures {self.symbol}:{self.contract}")

            df = self._clean_historical_data(raw_df)

            if self.interval_multiplier > 1:
                df = self._resample_data(df, self.interval, self.interval_multiplier)

            return df

        except Exception as e:
            raise ValueError(f"Failed to fetch futures historical data from efinance: {str(e)}") from e

    def _get_quote_id(self) -> str:
        """Convert symbol and contract to efinance quote_id format

        efinance uses format like "115.ZCM" where:
        - 115 is the contract code
        - ZCM indicates Zhengzhou Commodity Exchange

        For main contracts, we need to find the current main contract quote_id
        """
        if self.contract.lower() == "main":
            return self._get_main_contract_quote_id()

        contract_code = self.contract
        exchange_code = self._get_exchange_code()

        return f"{contract_code}.{exchange_code}"

    def _get_main_contract_quote_id(self) -> str:
        """Get quote_id for main contract"""
        try:
            base_info_df = ef.futures.get_futures_base_info()

            if base_info_df is None or base_info_df.empty:
                raise ValueError("Cannot get futures base info for main contract")

            symbol_upper = self.symbol.upper()

            matching_rows = base_info_df[base_info_df["期货代码"].str.contains(symbol_upper, case=False, na=False)]

            if matching_rows.empty:
                raise ValueError(f"Cannot find main contract for symbol {self.symbol}")

            main_row = matching_rows.iloc[0]
            quote_id = main_row.get("行情ID", "")

            if not quote_id:
                raise ValueError(f"Cannot get quote_id for main contract of {self.symbol}")

            return quote_id

        except Exception as e:
            raise ValueError(f"Failed to get main contract quote_id: {str(e)}") from e

    def _get_exchange_code(self) -> str:
        """Get exchange code prefix based on symbol"""
        symbol_upper = self.symbol.upper()

        SHFE_SYMBOLS = ["CU", "AL", "ZN", "PB", "NI", "SN", "SS", "AU", "AG", "RB", "WR", "HC", "SP", "FU", "BU"]
        DCE_SYMBOLS = [
            "C",
            "CS",
            "A",
            "M",
            "Y",
            "P",
            "B",
            "JD",
            "L",
            "V",
            "PP",
            "J",
            "JM",
            "I",
            "FB",
            "BB",
            "EG",
            "PG",
            "EB",
            "LH",
        ]
        CZCE_SYMBOLS = [
            "SR",
            "CF",
            "TA",
            "MA",
            "FG",
            "RM",
            "OI",
            "ZC",
            "JR",
            "RS",
            "PM",
            "WH",
            "AP",
            "UR",
            "SA",
            "PF",
            "PK",
            "CJ",
            "SF",
            "SM",
        ]
        CFFEX_SYMBOLS = ["IF", "IH", "IC", "IM", "TS", "TF", "T"]
        INE_SYMBOLS = ["SC", "NR", "LU"]

        if symbol_upper in SHFE_SYMBOLS:
            return "1"
        elif symbol_upper in DCE_SYMBOLS:
            return "2"
        elif symbol_upper in CZCE_SYMBOLS:
            return "3"
        elif symbol_upper in CFFEX_SYMBOLS:
            return "4"
        elif symbol_upper in INE_SYMBOLS:
            return "5"
        else:
            return "3"

    def _get_klt_parameter(self) -> int:
        """Convert interval to efinance klt parameter

        klt values:
        - 1: 1 minute
        - 5: 5 minutes
        - 15: 15 minutes
        - 30: 30 minutes
        - 60: 1 hour
        - 101: day
        - 102: week
        - 103: month
        """
        interval_map = {
            "minute": 1,
            "hour": 60,
            "day": 101,
            "week": 102,
            "month": 103,
        }

        return interval_map.get(self.interval, 101)

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format from YYYY-MM-DD to YYYYMMDD"""
        return date_str.replace("-", "") if "-" in date_str else date_str

    def _validate_interval_params(self, interval: str, multiplier: int) -> None:
        """Validates the validity of interval and multiplier"""
        if interval not in self.get_supported_intervals():
            raise ValueError(f"Unsupported interval parameter: {interval}")

        if interval in ["minute", "hour"] and multiplier < 1:
            raise ValueError(f"interval_multiplier for {interval} level must be >= 1")

    def _resample_data(self, df: pd.DataFrame, interval: str, multiplier: int) -> pd.DataFrame:
        """Resamples data to the specified interval"""
        freq_map = {
            "minute": f"{multiplier}min",
            "hour": f"{multiplier}h",
            "day": f"{multiplier}D",
            "week": f"{multiplier}W-MON",
            "month": f"{multiplier}MS",
        }
        freq = freq_map[interval]

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")

        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "open_interest": "last",
                "settlement": "last",
            }
        )
        return resampled.reset_index()

    def _clean_historical_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes historical data from efinance"""

        field_mapping = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "持仓量": "open_interest",
            "结算价": "settlement",
        }

        df = raw_df.copy()

        for src_field, target_field in field_mapping.items():
            if src_field in df.columns:
                df[target_field] = df[src_field]

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        df["symbol"] = self.symbol
        df["contract"] = self.contract

        if "open_interest" in df.columns:
            df["open_interest"] = df["open_interest"].fillna(0).astype("int64")

        if "settlement" not in df.columns:
            df["settlement"] = df.get("close", 0)

        standard_columns = [
            "timestamp",
            "symbol",
            "contract",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]

        result = df[[col for col in standard_columns if col in df.columns]]
        return result.reset_index(drop=True)

    def get_main_contracts(self) -> pd.DataFrame:
        """Fetches main contract list

        Returns:
            pd.DataFrame:
            - symbol: 期货代码
            - name: 期货名称
            - contract: 主力合约代码
            - exchange: 交易所
        """
        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance library is not installed. Please install it with: pip install efinance")

        try:
            base_info_df = ef.futures.get_futures_base_info()

            if base_info_df is None or base_info_df.empty:
                raise ValueError("No futures base info found")

            return self._clean_main_contracts(base_info_df)

        except Exception as e:
            raise ValueError(f"Failed to fetch main contracts from efinance: {str(e)}") from e

    def _clean_main_contracts(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes main contracts data from efinance"""

        df = raw_df.copy()

        field_mapping = {
            "期货代码": "symbol",
            "期货名称": "name",
            "合约代码": "contract",
            "交易所": "exchange",
        }

        for src_field, target_field in field_mapping.items():
            if src_field in df.columns:
                df[target_field] = df[src_field]

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.extract(r"^([A-Z]+)", expand=False).str.upper()

        if "exchange" not in df.columns:
            if "行情ID" in df.columns:
                df["exchange_code"] = df["行情ID"].astype(str).str.extract(r"\.([A-Z]+)$", expand=False)
                df["exchange"] = df["exchange_code"].map(_EXCHANGE_NAME_MAP).fillna("Unknown")

        required_columns = ["symbol", "name", "contract", "exchange"]
        result = df[[col for col in required_columns if col in df.columns]]

        if "name" not in result.columns and "symbol" in result.columns:
            result["name"] = result["symbol"]

        if "contract" not in result.columns and "symbol" in result.columns:
            result["contract"] = result["symbol"]

        return result.reset_index(drop=True)


def _build_cache_key(provider: "EfinanceFuturesRealtimeProvider") -> str:
    """Build cache key for EfinanceFuturesRealtimeProvider."""
    symbol_part = provider.symbol if provider.symbol else "all"
    contract_part = provider.contract if provider.contract else "all"
    return f"efinance_futures_{symbol_part}_{contract_part}"


@FuturesRealtimeFactory.register("efinance")
class EfinanceFuturesRealtimeProvider(RealtimeFuturesDataProvider):
    """Adapter for efinance futures realtime data API"""

    _API_MAP = {
        "get_current_data": {
            "ak_func": None,  # Direct efinance API call
        },
        "get_all_quotes": {
            "ak_func": None,  # Direct efinance API call
        },
    }

    def get_source_name(self) -> str:
        return "efinance"

    @cache("futures_realtime_cache", key=_build_cache_key)
    def get_current_data(self) -> pd.DataFrame:
        """Fetches realtime futures market data

        Returns:
            pd.DataFrame:
            - symbol: 期货代码
            - contract: 合约代码
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - timestamp: 时间戳
            - volume: 成交量
            - open_interest: 持仓量
            - open: 今开
            - high: 最高
            - low: 最低
            - prev_settlement: 昨结算
            - settlement: 最新结算价
        """
        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance library is not installed. Please install it with: pip install efinance")

        try:
            raw_df = ef.futures.get_realtime_quotes()

            if raw_df is None or raw_df.empty:
                raise ValueError("No realtime futures quotes found")

            df = self._clean_realtime_data(raw_df)

            if self.symbol:
                symbol_upper = self.symbol.upper()

                if self.contract and self.contract.lower() != "main":
                    full_symbol = f"{symbol_upper}{self.contract}"
                    if "symbol" in df.columns:
                        df = df[df["symbol"] == full_symbol].reset_index(drop=True)
                else:
                    if "symbol_root" in df.columns:
                        df = df[df["symbol_root"] == symbol_upper].reset_index(drop=True)
                    elif "symbol" in df.columns:
                        df = df[df["symbol"].str.startswith(symbol_upper)].reset_index(drop=True)

            return df

        except Exception as e:
            raise ValueError(f"Failed to fetch realtime futures data from efinance: {str(e)}") from e

    def get_all_quotes(self) -> pd.DataFrame:
        """Fetches all futures quotes

        Returns:
            pd.DataFrame: All futures market quotes
        """
        return self.get_current_data()

    def _clean_realtime_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes realtime futures data from efinance"""

        field_mapping = {
            "期货代码": "symbol",
            "期货名称": "name",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "昨结算": "prev_settlement",
            "结算价": "settlement",
            "成交量": "volume",
            "持仓量": "open_interest",
            "行情ID": "quote_id",
        }

        df = raw_df.copy()

        for src_field, target_field in field_mapping.items():
            if src_field in df.columns:
                df[target_field] = df[src_field]

        df = df.assign(
            timestamp=pd.Timestamp.now(tz="Asia/Shanghai"),
        )

        if "pct_change" not in df.columns and "change" in df.columns and "prev_settlement" in df.columns:
            df["pct_change"] = (df["change"] / df["prev_settlement"] * 100).round(2)

        if "settlement" not in df.columns:
            df["settlement"] = df.get("price", 0)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()
            df["symbol_root"] = df["symbol"].str.extract(r"^([A-Z]+)", expand=False)
            df["contract"] = df["symbol"].str.extract(r"([0-9]+)$", expand=False).fillna("")

        required_columns = [
            "symbol",
            "symbol_root",
            "contract",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "open_interest",
            "open",
            "high",
            "low",
            "prev_settlement",
            "settlement",
        ]

        result = df[[col for col in required_columns if col in df.columns]]
        return result.reset_index(drop=True)


EfinanceFuturesHistorical = EfinanceFuturesHistoricalProvider
EfinanceFuturesRealtime = EfinanceFuturesRealtimeProvider
