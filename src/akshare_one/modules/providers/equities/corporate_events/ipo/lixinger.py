"""
Lixinger provider for IPO / new-listing data.

Uses cn/company endpoint to query company basic info and filter by listing
date, providing a backup source for get_new_stocks.

Note: Lixinger does not expose a dedicated IPO-subscription summary API,
so get_ipo_info is not supported and returns an empty DataFrame.
"""

import time

import pandas as pd

from ......lixinger_client import get_lixinger_client
from ......metrics.stats import get_stats_collector
from ......constants import SYMBOL_ZFILL_WIDTH
from .base import IPOFactory, IPOProvider


@IPOFactory.register("lixinger")
class LixingerIPOProvider(IPOProvider):
    """
    IPO data provider using Lixinger OpenAPI.

    get_new_stocks  → cn/company  (filter by listingDate range)
    get_ipo_info    → not supported (returns empty DataFrame)
    """

    def get_source_name(self) -> str:
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_new_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get newly listed A-share stocks from Lixinger.

        Fetches all companies from cn/company and filters by listingDate.
        cn/company does not support date-range filtering, so we fetch all
        and filter client-side.

        Returns:
            pd.DataFrame with columns:
                symbol, name, ipo_date, market, area_code
        """
        import datetime

        start_time = time.time()

        try:
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")

            if not end_date:
                end_date = datetime.date.today().strftime("%Y-%m-%d")
            if not start_date:
                start_dt = datetime.date.today() - datetime.timedelta(days=365)
                start_date = start_dt.strftime("%Y-%m-%d")

            client = get_lixinger_client()
            all_data = []
            page = 0

            # cn/company is paginated; fetch all pages
            while True:
                params = {"pageIndex": page}
                response = client.query_api("cn/company", params)
                if response.get("code") != 1:
                    self.logger.warning(f"Lixinger cn/company error: {response.get('msg')}")
                    break
                data = response.get("data", [])
                if not data:
                    break
                all_data.extend(data)
                # If fewer records than a typical page, we're done
                if len(data) < 100:
                    break
                page += 1

            if not all_data:
                return self.create_empty_dataframe(["symbol", "name", "ipo_date", "market", "area_code"])

            df = pd.DataFrame(all_data)
            out = self._standardize_new_stocks(df)

            # Filter by date range client-side
            if "ipo_date" in out.columns and out["ipo_date"].notna().any():
                mask = (out["ipo_date"] >= start_date) & (out["ipo_date"] <= end_date)
                out = out[mask].reset_index(drop=True)

            result = self.standardize_and_filter(out, source="lixinger", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("lixinger", duration_ms, True)

            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("lixinger", duration_ms, False)
            raise

    def _standardize_new_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()

        if "stockCode" in df.columns:
            out["symbol"] = df["stockCode"].astype(str).str.zfill(SYMBOL_ZFILL_WIDTH)
        else:
            out["symbol"] = ""

        if "cnName" in df.columns:
            out["name"] = df["cnName"].astype(str)
        else:
            out["name"] = ""

        if "listingDate" in df.columns:
            out["ipo_date"] = pd.to_datetime(df["listingDate"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            out["ipo_date"] = ""

        if "market" in df.columns:
            out["market"] = df["market"].astype(str)
        else:
            out["market"] = ""

        if "areaCode" in df.columns:
            out["area_code"] = df["areaCode"].astype(str)
        else:
            out["area_code"] = ""

        out = out.sort_values("ipo_date", ascending=False, na_position="last").reset_index(drop=True)
        return self.ensure_json_compatible(out)

    def get_ipo_info(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Lixinger does not provide IPO subscription summary data.
        Returns empty DataFrame.
        """
        self.logger.warning(
            "Lixinger does not support IPO subscription info (get_ipo_info). Use eastmoney source for this query."
        )
        return self.create_empty_dataframe(["symbol", "name", "ipo_date", "underwriter", "industry"])
