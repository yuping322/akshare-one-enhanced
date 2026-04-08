"""
TickFlow provider for market infrastructure data.

This module implements instrument, exchange, and universe data providers using TickFlow API.
"""

import pandas as pd

from ...tickflow_client import get_tickflow_client
from .base import (
    ExchangeFactory,
    ExchangeProvider,
    InstrumentFactory,
    InstrumentProvider,
    UniverseFactory,
    UniverseProvider,
)


@InstrumentFactory.register("tickflow")
class TickFlowInstrumentProvider(InstrumentProvider):
    """
    Instrument metadata provider using TickFlow API.

    Provides metadata for stocks, ETFs, indices, etc.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_instruments(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get instrument metadata from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Instrument metadata with columns:
                - symbol: Instrument code
                - name: Instrument name
                - exchange: Exchange code
                - type: Instrument type (stock, etf, index, etc.)
                - status: Instrument status
                - listing_date: Listing date
        """
        client = get_tickflow_client()

        symbols = kwargs.get("symbols", self.symbols)

        if symbols and isinstance(symbols, list):
            if len(symbols) <= 20:
                symbols_str = ",".join(symbols)
                params = {"symbols": symbols_str}
                response = client.query_api("/v1/instruments", method="GET", params=params)
            else:
                data = {"symbols": symbols}
                response = client.query_api("/v1/instruments", method="POST", data=data)
        elif symbols:
            params = {"symbols": symbols}
            response = client.query_api("/v1/instruments", method="GET", params=params)
        else:
            return pd.DataFrame()

        instruments = response.get("data", [])
        if not instruments:
            return pd.DataFrame()

        df = pd.DataFrame(instruments)

        if "ext" in df.columns:
            ext_data = df["ext"].apply(lambda x: x if isinstance(x, dict) else {})
            ext_df = pd.DataFrame(ext_data.tolist())

            for col in ext_df.columns:
                if col not in df.columns and col != "type":
                    df[col] = ext_df[col]

            df.drop(columns=["ext"], errors="ignore", inplace=True)

        if "code" in df.columns and "symbol" not in df.columns:
            df = df.rename(columns={"code": "symbol"})

        df = self.ensure_json_compatible(df)

        if row_filter:
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        elif columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df


@ExchangeFactory.register("tickflow")
class TickFlowExchangeProvider(ExchangeProvider):
    """
    Exchange data provider using TickFlow API.

    Provides exchange list and instruments for each exchange.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_exchanges(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get exchange list from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Exchange list with columns:
                - code: Exchange code (SH, SZ, BJ, US, HK)
                - name: Exchange name
                - instrument_count: Number of instruments
        """
        client = get_tickflow_client()

        response = client.query_api("/v1/exchanges", method="GET")

        exchanges = response.get("data", [])
        if not exchanges:
            return pd.DataFrame()

        df = pd.DataFrame(exchanges)

        column_rename = {
            "code": "exchange",
            "count": "instrument_count",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        df = self.ensure_json_compatible(df)

        if row_filter:
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        elif columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df

    def get_exchange_instruments(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get instruments for a specific exchange from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - type: Instrument type filter (stock, etf, index, etc.)

        Returns:
            pd.DataFrame: Instruments for the exchange
        """
        client = get_tickflow_client()

        exchange = kwargs.get("exchange", self.exchange)
        if not exchange:
            return pd.DataFrame()

        params = {}
        instrument_type = kwargs.get("type")
        if instrument_type:
            params["type"] = instrument_type

        endpoint = f"/v1/exchanges/{exchange}/instruments"
        response = client.query_api(endpoint, method="GET", params=params)

        instruments = response.get("data", [])
        if not instruments:
            return pd.DataFrame()

        df = pd.DataFrame(instruments)

        if "ext" in df.columns:
            ext_data = df["ext"].apply(lambda x: x if isinstance(x, dict) else {})
            ext_df = pd.DataFrame(ext_data.tolist())

            for col in ext_df.columns:
                if col not in df.columns and col != "type":
                    df[col] = ext_df[col]

            df.drop(columns=["ext"], errors="ignore", inplace=True)

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)


@UniverseFactory.register("tickflow")
class TickFlowUniverseProvider(UniverseProvider):
    """
    Universe (标的池) data provider using TickFlow API.

    Provides universe list and details.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_universes(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get universe list from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Universe list with columns:
                - id: Universe ID
                - name: Universe name
                - description: Universe description
                - instrument_count: Number of instruments
        """
        client = get_tickflow_client()

        response = client.query_api("/v1/universes", method="GET")

        universes = response.get("data", [])
        if not universes:
            return pd.DataFrame()

        df = pd.DataFrame(universes)

        df = self.ensure_json_compatible(df)

        if row_filter:
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        elif columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df

    def get_universe_detail(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get universe detail from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Universe detail with instruments list
        """
        client = get_tickflow_client()

        universe_id = kwargs.get("universe_id", self.universe_id)
        if not universe_id:
            return pd.DataFrame()

        endpoint = f"/v1/universes/{universe_id}"
        response = client.query_api(endpoint, method="GET")

        universe_data = response.get("data", {})
        if not universe_data:
            return pd.DataFrame()

        instruments = universe_data.get("instruments", [])
        if not instruments:
            df = pd.DataFrame([universe_data])
            df = self.ensure_json_compatible(df)
            if row_filter:
                df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
            elif columns:
                available_cols = [col for col in columns if col in df.columns]
                if available_cols:
                    df = df[available_cols]
            return df

        df = pd.DataFrame(instruments)

        df["universe_id"] = universe_id
        df["universe_name"] = universe_data.get("name")

        df = self.ensure_json_compatible(df)

        if row_filter:
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        elif columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df

    def get_universes_batch(
        self, universe_ids: list[str], columns: list | None = None, row_filter: dict | None = None
    ) -> pd.DataFrame:
        """
        Get multiple universe details in batch.

        Args:
            universe_ids: List of universe IDs
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Combined universe details
        """
        client = get_tickflow_client()

        data = {"ids": universe_ids}
        response = client.query_api("/v1/universes/batch", method="POST", data=data)

        universes = response.get("data", [])
        if not universes:
            return pd.DataFrame()

        all_instruments = []
        for universe in universes:
            if isinstance(universe, dict):
                instruments = universe.get("instruments", [])
                for inst in instruments:
                    if isinstance(inst, dict):
                        inst["universe_id"] = universe.get("id")
                        inst["universe_name"] = universe.get("name")
                        all_instruments.append(inst)

        if not all_instruments:
            df = pd.DataFrame([u for u in universes if isinstance(u, dict)])
            df = self.ensure_json_compatible(df)
            if row_filter:
                df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
            elif columns:
                available_cols = [col for col in columns if col in df.columns]
                if available_cols:
                    df = df[available_cols]
            return df

        df = pd.DataFrame(all_instruments)

        df = self.ensure_json_compatible(df)

        if row_filter:
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        elif columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]

        return df
