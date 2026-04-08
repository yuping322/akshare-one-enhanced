"""
Tushare Pro client adapter.

This module provides a unified interface for accessing Tushare Pro API.
"""

from typing import Any, Optional

import pandas as pd

from .error_codes import ErrorCode
from .logging_config import get_logger
from .modules.exceptions import DataSourceUnavailableError, RateLimitError
from .tushare_config import get_tushare_config, has_tushare_api_key


class TushareClient:
    """Tushare Pro API client wrapper."""

    _instance: Optional["TushareClient"] = None
    _pro: Any | None = None

    def __new__(cls) -> "TushareClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize Tushare Pro client."""
        self.logger = get_logger(__name__)

        if not has_tushare_api_key():
            self.logger.warning("Tushare API key not configured. Please set it using set_tushare_api_key()")
            return

        try:
            import tushare as ts

            api_key = get_tushare_config().get_api_key()
            if api_key:
                ts.set_token(api_key)
                self._pro = ts.pro_api()
                self.logger.info("Tushare Pro API initialized successfully")
        except ImportError:
            self.logger.error("tushare package not installed. Install with: pip install tushare")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tushare Pro API: {e}")

    def is_available(self) -> bool:
        """Check if Tushare API is available."""
        return self._pro is not None

    def query(self, api_name: str, **kwargs) -> pd.DataFrame:
        """
        Query Tushare Pro API.

        Args:
            api_name: Tushare API name (e.g., 'daily', 'income', 'balancesheet')
            **kwargs: API parameters

        Returns:
            DataFrame with query results

        Raises:
            DataSourceUnavailableError: If API is not available
            RateLimitError: If API rate limit exceeded
        """
        if not self.is_available():
            raise DataSourceUnavailableError(
                "Tushare Pro API not available. Please configure API key and ensure tushare package is installed.",
                error_code=ErrorCode.SOURCE_UNAVAILABLE,
                context={"source": "tushare"},
            )

        try:
            self.logger.debug(f"Querying Tushare API: {api_name} with params: {kwargs}")
            df = self._pro.query(api_name, **kwargs)
            self.logger.debug(f"Tushare API returned {len(df)} rows")
            return df
        except Exception as e:
            error_msg = str(e)

            if "您没有权限访问此接口" in error_msg or "没有权限" in error_msg:
                raise DataSourceUnavailableError(
                    f"No permission to access Tushare API '{api_name}'. {error_msg}",
                    error_code=ErrorCode.SOURCE_UNAVAILABLE,
                    context={"source": "tushare", "api_name": api_name},
                ) from None
            elif "每分钟最多访问" in error_msg or "超过访问限制" in error_msg:
                raise RateLimitError(
                    f"Tushare API rate limit exceeded for '{api_name}'. {error_msg}",
                    error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                    context={"source": "tushare", "api_name": api_name},
                ) from None
            else:
                self.logger.error(f"Tushare API query failed for '{api_name}': {e}")
                raise DataSourceUnavailableError(
                    f"Tushare API query failed for '{api_name}': {error_msg}",
                    error_code=ErrorCode.SOURCE_UNAVAILABLE,
                    context={"source": "tushare", "api_name": api_name},
                ) from None

    def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """Get stock basic info."""
        return self.query("stock_basic", **kwargs)

    def get_trade_cal(self, **kwargs) -> pd.DataFrame:
        """Get trade calendar."""
        return self.query("trade_cal", **kwargs)

    def get_daily(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get daily price data."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("daily", **params)

    def get_income(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get income statement."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("income", **params)

    def get_balancesheet(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get balance sheet."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("balancesheet", **params)

    def get_cashflow(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get cash flow statement."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("cashflow", **params)

    def get_fina_indicator(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get financial indicators."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("fina_indicator", **params)

    def get_daily_basic(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get daily basic indicators (PE, PB, turnover rate, etc.)."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("daily_basic", **params)

    def get_suspend(
        self,
        ts_code: str | None = None,
        suspend_date: str | None = None,
        resume_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get suspension/resumption data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if suspend_date:
            params["suspend_date"] = suspend_date
        if resume_date:
            params["resume_date"] = resume_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("suspend", **params)

    def get_dividend(
        self,
        ts_code: str | None = None,
        ann_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get dividend data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if ann_date:
            params["ann_date"] = ann_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("dividend", **params)

    def get_forecast(
        self,
        ts_code: str | None = None,
        ann_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get performance forecast data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if ann_date:
            params["ann_date"] = ann_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("forecast", **params)

    def get_express(
        self,
        ts_code: str | None = None,
        ann_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get performance express (quick report) data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if ann_date:
            params["ann_date"] = ann_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("express", **params)

    def get_stk_limit(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get daily limit up/down prices."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("stk_limit", **params)

    def get_adj_factor(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get adjustment factor data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("adj_factor", **params)

    def get_top_list(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get dragon tiger list daily details."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("top_list", **params)

    def get_top_inst(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get institutional trading details from dragon tiger list."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("top_inst", **params)

    def get_margin(
        self,
        trade_date: str | None = None,
        ts_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        exchange: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get margin financing summary data."""
        params = {}
        if trade_date:
            params["trade_date"] = trade_date
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if exchange:
            params["exchange"] = exchange
        params.update(kwargs)
        return self.query("margin", **params)

    def get_margin_detail(
        self,
        trade_date: str | None = None,
        ts_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get margin financing detail data for individual stocks."""
        params = {}
        if trade_date:
            params["trade_date"] = trade_date
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("margin_detail", **params)

    def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """Get index basic info."""
        return self.query("index_basic", **kwargs)

    def get_index_daily(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get index daily data."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("index_daily", **params)

    def get_index_weight(
        self, index_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get index constituent weights."""
        params = {"index_code": index_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("index_weight", **params)

    def get_index_dailybasic(
        self,
        ts_code: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get index daily basic indicators."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("index_dailybasic", **params)

    def get_top10_holders(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get top 10 shareholders."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("top10_holders", **params)

    def get_top10_floatholders(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get top 10 float shareholders."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("top10_floatholders", **params)

    def get_stk_holdernumber(
        self, ts_code: str, start_date: str | None = None, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get shareholder number."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("stk_holdernumber", **params)

    def get_stk_holdertrade(
        self,
        ts_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get shareholder trade records."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("stk_holdertrade", **params)

    def get_moneyflow_hkctl(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get northbound capital flow (沪深港通资金流向)."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("moneyflow_hkctl", **params)

    def get_hk_hold(
        self,
        ts_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get northbound holdings details (沪深股通持股明细)."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("hk_hold", **params)

    def get_hk_top10(
        self,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get top 10 stocks traded by northbound capital (沪深股通十大成交股)."""
        params = {}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("hk_top10", **params)

    def get_ggt_top10(
        self,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get top 10 stocks traded by southbound capital (港股通十大成交股)."""
        params = {}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("ggt_top10", **params)

    def get_shibor(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get Shibor (Shanghai Interbank Offered Rate) data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("shibor", **params)

    def get_lpr(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get LPR (Loan Prime Rate) data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("lpr_data", **params)

    def get_gdp_monthly(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get GDP monthly data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("gdp_monthly", **params)

    def get_cpi(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get CPI (Consumer Price Index) data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("cpi_monthly", **params)

    def get_ppi(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get PPI (Producer Price Index) data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("ppi_monthly", **params)

    def get_pmi(self, start_date: str | None = None, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """Get PMI (Purchasing Managers' Index) data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("pmi_monthly", **params)

    def get_share_pledge(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get share pledge statistics."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("share_pledge", **params)

    def get_pledge_detail(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get pledge detail data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("pledge_detail", **params)

    def get_share_float(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get restricted share float data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("share_float", **params)

    def get_block_trade(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get block trade data."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("block_trade", **params)

    def get_cyq_chips(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get chip distribution data."""
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("cyq_chips", **params)

    def get_stk_factor(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get stock factor data (broker profit forecast)."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("stk_factor", **params)

    def get_stk_research(
        self,
        ts_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get stock research data (institutional research)."""
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        params.update(kwargs)
        return self.query("stk_research", **params)


def get_tushare_client() -> TushareClient:
    """Get the singleton TushareClient instance."""
    return TushareClient()
