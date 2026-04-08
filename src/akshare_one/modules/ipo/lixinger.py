"""
Lixinger provider for IPO / new-listing data.

Uses cn/company endpoint to query company basic info and filter by listing
date, providing a backup source for get_new_stocks.

Note: Lixinger does not expose a dedicated IPO-subscription summary API,
so get_ipo_info is not supported and returns an empty DataFrame.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
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

        Queries cn/company for all companies and filters those whose
        listingDate falls within the last 365 days (or a custom range
        passed via kwargs start_date / end_date).

        Returns:
            pd.DataFrame with columns:
                symbol, name, ipo_date, market, area_code
        """
        import datetime

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        if not end_date:
            end_date = datetime.date.today().strftime("%Y-%m-%d")
        if not start_date:
            # default: last 365 days
            start_dt = datetime.date.today() - datetime.timedelta(days=365)
            start_date = start_dt.strftime("%Y-%m-%d")

        client = get_lixinger_client()
        params = {
            "listingDateStart": start_date,
            "listingDateEnd": end_date,
        }

        response = client.query_api("cn/company", params)

        if response.get("code") != 1:
            self.logger.warning(
                f"Lixinger cn/company returned error: {response.get('msg')}"
            )
            return self.create_empty_dataframe(
                ["symbol", "name", "ipo_date", "market", "area_code"]
            )

        data = response.get("data", [])
        if not data:
            return self.create_empty_dataframe(
                ["symbol", "name", "ipo_date", "market", "area_code"]
            )

        df = pd.DataFrame(data)
        out = self._standardize_new_stocks(df)

        return self.standardize_and_filter(
            out, source="lixinger", columns=columns, row_filter=row_filter
        )

    def _standardize_new_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()

        if "stockCode" in df.columns:
            out["symbol"] = df["stockCode"].astype(str).str.zfill(6)
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
            "Lixinger does not support IPO subscription info (get_ipo_info). "
            "Use eastmoney source for this query."
        )
        return self.create_empty_dataframe(
            ["symbol", "name", "ipo_date", "underwriter", "industry"]
        )
