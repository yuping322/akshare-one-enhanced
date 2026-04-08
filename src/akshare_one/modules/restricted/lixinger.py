"""
Lixinger provider for restricted stock release data.

Uses cn/company/restricted-release API to provide lock-up expiry data
as a backup to the eastmoney source.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import RestrictedReleaseFactory, RestrictedReleaseProvider


@RestrictedReleaseFactory.register("lixinger")
class LixingerRestrictedReleaseProvider(RestrictedReleaseProvider):
    """
    Restricted stock release data provider using Lixinger OpenAPI.

    Covers cn/company/restricted-release endpoint.
    """

    def get_source_name(self) -> str:
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_restricted_release(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get restricted stock release data from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, not supported by
                    Lixinger API — returns empty DataFrame.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame with columns:
                symbol, release_date, release_shares, release_value,
                release_type, shareholder_name
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        # Lixinger requires a stockCode; market-wide query not supported
        if not symbol:
            self.logger.warning(
                "Lixinger restricted-release API requires a stock symbol. "
                "Market-wide query is not supported. Returning empty DataFrame."
            )
            return self.create_empty_dataframe(
                ["symbol", "release_date", "release_shares", "release_value",
                 "release_type", "shareholder_name"]
            )

        client = get_lixinger_client()
        params = {
            "stockCode": symbol,
            "startDate": start_date,
            "endDate": end_date,
        }

        response = client.query_api("cn/company/restricted-release", params)

        if response.get("code") != 1:
            self.logger.warning(
                f"Lixinger restricted-release returned error for {symbol}: "
                f"{response.get('msg')}"
            )
            return self.create_empty_dataframe(
                ["symbol", "release_date", "release_shares", "release_value",
                 "release_type", "shareholder_name"]
            )

        data = response.get("data", [])
        if not data:
            return self.create_empty_dataframe(
                ["symbol", "release_date", "release_shares", "release_value",
                 "release_type", "shareholder_name"]
            )

        df = pd.DataFrame(data)
        return self._standardize(df, symbol)

    def _standardize(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Map Lixinger fields to the standard schema."""
        out = pd.DataFrame()
        out["symbol"] = symbol.zfill(6)

        # date field from Lixinger is ISO-8601
        if "date" in df.columns:
            out["release_date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            out["release_date"] = ""

        # shares count
        if "restrictedSharesReleased" in df.columns:
            out["release_shares"] = pd.to_numeric(df["restrictedSharesReleased"], errors="coerce")
        else:
            out["release_shares"] = 0.0

        # market value (元)
        if "restrictedSharesReleasedMarketValue" in df.columns:
            out["release_value"] = pd.to_numeric(df["restrictedSharesReleasedMarketValue"], errors="coerce")
        else:
            out["release_value"] = 0.0

        # share type / release type
        if "restrictedSharesType" in df.columns:
            out["release_type"] = df["restrictedSharesType"].astype(str)
        else:
            out["release_type"] = ""

        # shareholder name
        if "shareholderName" in df.columns:
            out["shareholder_name"] = df["shareholderName"].astype(str)
        else:
            out["shareholder_name"] = ""

        out = out.sort_values("release_date", na_position="last").reset_index(drop=True)
        return self.ensure_json_compatible(out)

    def get_restricted_release_calendar(
        self,
        start_date: str,
        end_date: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Lixinger does not provide a market-wide release calendar endpoint.
        Returns empty DataFrame.
        """
        self.logger.warning(
            "Lixinger does not support market-wide restricted release calendar. "
            "Use eastmoney source for this query."
        )
        return self.create_empty_dataframe(
            ["date", "release_stock_count", "total_release_value"]
        )
