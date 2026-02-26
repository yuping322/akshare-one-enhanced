"""
Sina/Eastmoney options data provider.

This module implements the options data provider using option_current_em as the data source.
Note: The original sina APIs (option_sse_list_sina, etc.) are broken, so we use eastmoney APIs.
"""

import re
from datetime import datetime

import akshare as ak
import numpy as np
import pandas as pd

from mappings.mapping_utils import get_option_underlying_patterns

from ..cache import cache
from .base import OptionsDataProvider


class SinaOptionsProvider(OptionsDataProvider):
    """Adapter for Sina/EastMoney options data API.

    Note: Uses option_current_em from eastmoney as the primary data source
    since the original sina APIs are broken.
    """

    def ensure_json_compatible(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure DataFrame is JSON compatible by replacing NaN/Infinity with None."""
        df = df.copy()
        for col in df.columns:
            if df[col].dtype in ["float64", "float32", "int64", "int32"]:
                df[col] = df[col].replace({np.nan: None, np.inf: None, -np.inf: None})
            elif df[col].dtype == "object":
                df[col] = df[col].replace({np.nan: None})
        return df

    @cache(
        "options_chain_cache",
        key=lambda self: f"sina_options_chain_{self.underlying_symbol}",
    )
    def get_options_chain(self) -> pd.DataFrame:
        """Fetches options chain data

        Returns:
            pd.DataFrame:
            - underlying: 标的代码
            - symbol: 期权代码
            - name: 期权名称
            - option_type: 期权类型 (call/put)
            - strike: 行权价
            - expiration: 到期日
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - volume: 成交量
            - open_interest: 持仓量
            - implied_volatility: 隐含波动率
        """
        try:
            # Get all options data from eastmoney
            raw_df = ak.option_current_em()

            if raw_df.empty:
                raise ValueError("No options data available")

            # Filter by underlying symbol
            patterns = get_option_underlying_patterns(self.underlying_symbol)
            pattern_regex = "|".join(patterns)
            df = raw_df[raw_df["名称"].str.contains(pattern_regex, na=False, regex=True)].copy()

            if df.empty:
                raise ValueError(f"No options found for underlying symbol: {self.underlying_symbol}")

            # Parse option info from names
            df["option_type"] = df["名称"].apply(self._parse_option_type)
            df["expiration"] = df["名称"].apply(self._parse_expiration)
            df["underlying"] = self.underlying_symbol

            # Rename columns
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌额": "change",
                    "涨跌幅": "pct_change",
                    "成交量": "volume",
                    "持仓量": "open_interest",
                    "行权价": "strike",
                }
            )

            # Add placeholder for implied volatility
            df["implied_volatility"] = None

            # Select and order columns
            standard_columns = [
                "underlying",
                "symbol",
                "name",
                "option_type",
                "strike",
                "expiration",
                "price",
                "change",
                "pct_change",
                "volume",
                "open_interest",
                "implied_volatility",
            ]

            result = df[[col for col in standard_columns if col in df.columns]].copy()
            return self.ensure_json_compatible(result)
        except Exception as e:
            raise ValueError(f"Failed to fetch options chain: {str(e)}") from e

    @cache(
        "options_realtime_cache",
        key=lambda self, symbol: f"sina_options_realtime_{symbol}",
    )
    def get_options_realtime(self, symbol: str) -> pd.DataFrame:
        """Fetches realtime options quote data

        Args:
            symbol: 期权代码 (e.g., '10010459'), 传空字符串则获取该标的下的所有期权

        Returns:
            pd.DataFrame:
            - symbol: 期权代码
            - underlying: 标的代码
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - timestamp: 时间戳
            - volume: 成交量
            - open_interest: 持仓量
            - iv: 隐含波动率
        """
        try:
            # Get all options data from eastmoney
            raw_df = ak.option_current_em()

            if not symbol:
                # Get all options for the underlying
                patterns = get_option_underlying_patterns(self.underlying_symbol)
                pattern_regex = "|".join(patterns)
                df = raw_df[raw_df["名称"].str.contains(pattern_regex, na=False, regex=True)].copy()
            else:
                # Get specific option by symbol
                df = raw_df[raw_df["代码"] == symbol].copy()

            if df.empty:
                return pd.DataFrame(
                    columns=[
                        "symbol",
                        "underlying",
                        "price",
                        "change",
                        "pct_change",
                        "timestamp",
                        "volume",
                        "open_interest",
                        "iv",
                    ]
                )

            # Rename columns
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "最新价": "price",
                    "涨跌额": "change",
                    "涨跌幅": "pct_change",
                    "成交量": "volume",
                    "持仓量": "open_interest",
                }
            )

            df["underlying"] = self.underlying_symbol
            df["timestamp"] = datetime.now()
            df["iv"] = None

            # Select columns
            standard_columns = [
                "symbol",
                "underlying",
                "price",
                "change",
                "pct_change",
                "timestamp",
                "volume",
                "open_interest",
                "iv",
            ]

            result = df[[col for col in standard_columns if col in df.columns]].copy()
            return self.ensure_json_compatible(result)
        except Exception as e:
            raise ValueError(f"Failed to fetch options realtime data: {str(e)}") from e

    def get_options_expirations(self, underlying_symbol: str) -> list[str]:
        """Fetches available expiration dates for options

        Args:
            underlying_symbol: 标的代码

        Returns:
            list[str]: 可用的到期日列表
        """
        try:
            # Get all options data from eastmoney
            raw_df = ak.option_current_em()

            # Filter by underlying symbol
            patterns = get_option_underlying_patterns(underlying_symbol)
            pattern_regex = "|".join(patterns)
            df = raw_df[raw_df["名称"].str.contains(pattern_regex, na=False, regex=True)].copy()

            if df.empty:
                raise ValueError(f"No options found for underlying symbol: {underlying_symbol}")

            # Extract unique expirations
            expirations = df["名称"].apply(self._parse_expiration).dropna().unique().tolist()
            return sorted(expirations)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to fetch options expirations: {str(e)}") from e

    def get_options_history(
        self,
        symbol: str,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """Fetches options historical data

        Args:
            symbol: 期权代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame:
            - timestamp: 时间戳
            - symbol: 期权代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - open_interest: 持仓量
            - settlement: 结算价
        """
        try:
            raw_df = ak.option_sse_daily_sina(symbol=symbol)

            if raw_df.empty:
                return pd.DataFrame(
                    columns=[
                        "timestamp",
                        "symbol",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "open_interest",
                        "settlement",
                    ]
                )

            # Filter by date range
            raw_df["日期"] = pd.to_datetime(raw_df["日期"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            raw_df = raw_df[(raw_df["日期"] >= start_dt) & (raw_df["日期"] <= end_dt)]

            return self._clean_options_history(raw_df, symbol)
        except Exception as e:
            raise ValueError(f"Failed to fetch options history: {str(e)}") from e

    def _parse_option_type(self, name: str) -> str | None:
        """Parse option type (call/put) from name."""
        if "购" in name:
            return "call"
        elif "沽" in name:
            return "put"
        return None

    def _parse_expiration(self, name: str) -> str | None:
        """Parse expiration from name (e.g., '300ETF沽2月4288A' -> '2月')."""
        match = re.search(r"(\d+月)", name)
        if match:
            return match.group(1)
        return None

    def _clean_options_history(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Cleans and standardizes options historical data"""
        column_map = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }

        available_columns = {src: target for src, target in column_map.items() if src in raw_df.columns}

        if not available_columns:
            raise ValueError("Expected columns not found in options history data")

        df = raw_df.rename(columns=available_columns)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        df["symbol"] = symbol

        # Add placeholder columns for missing data
        if "open_interest" not in df.columns:
            df["open_interest"] = None
        if "settlement" not in df.columns:
            df["settlement"] = None

        # Convert numeric columns
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self._select_history_columns(df)

    def _select_history_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard options history columns"""
        standard_columns = [
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]
        return df[[col for col in standard_columns if col in df.columns]]
