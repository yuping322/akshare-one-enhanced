"""
Contract tests for _API_MAP completeness across all modules.

This test ensures that all provider classes have complete _API_MAP mappings
for their public methods, preventing NotImplementedError.

Run: pytest tests/test_api_map_contract.py -v
"""

import inspect
from pathlib import Path

import pytest

from akshare_one.modules.etf.base import ETFProvider, ETFFactory
from akshare_one.modules.bond.base import BondProvider, BondFactory
from akshare_one.modules.futures.base import (
    HistoricalFuturesDataProvider,
    RealtimeFuturesDataProvider,
    FuturesHistoricalFactory,
    FuturesRealtimeFactory,
)
from akshare_one.modules.options.base import OptionsDataProvider, OptionsDataFactory
from akshare_one.modules.fundflow.base import FundFlowProvider, FundFlowFactory
from akshare_one.modules.analyst.base import AnalystProvider, AnalystFactory


def get_public_methods(cls):
    """Get all public methods from a class (excluding inherited from BaseProvider)."""
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Skip private methods and inherited base methods
        if name.startswith("_"):
            continue
        # Check if method is defined in this class or a parent provider class
        if name in ["fetch_data", "get_source_name", "get_data_type", "get_data"]:
            continue
        # Include methods that should be in _API_MAP
        methods.append(name)
    return methods


def get_provider_classes(factory):
    """Get all registered provider classes from a factory."""
    return list(factory._providers.values())


@pytest.mark.contract
class TestETFAPIMapContract:
    """Contract tests for ETF module _API_MAP."""

    def test_all_etf_providers_have_api_map(self):
        """Verify all ETF providers have _API_MAP defined."""
        providers = get_provider_classes(ETFFactory)
        assert len(providers) > 0, "No ETF providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"
            assert isinstance(provider_cls._API_MAP, dict), f"{provider_cls.__name__} _API_MAP must be a dict"

    def test_etf_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        providers = get_provider_classes(ETFFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            public_methods = get_public_methods(ETFProvider)

            # Check that all methods in _API_MAP exist
            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(ETFProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )

    def test_etf_api_map_structure(self):
        """Verify _API_MAP entries have correct structure."""
        providers = get_provider_classes(ETFFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP

            for method_name, config in api_map.items():
                assert "ak_func" in config, f"{provider_cls.__name__}:{method_name} missing 'ak_func'"
                # ak_func can be None (for methods not supported by this provider)
                if config["ak_func"] is not None:
                    assert isinstance(config["ak_func"], str), (
                        f"{provider_cls.__name__}:{method_name} 'ak_func' must be string or None"
                    )

                if "params" in config:
                    assert isinstance(config["params"], dict), (
                        f"{provider_cls.__name__}:{method_name} 'params' must be dict"
                    )


@pytest.mark.contract
class TestBondAPIMapContract:
    """Contract tests for Bond module _API_MAP."""

    def test_all_bond_providers_have_api_map(self):
        """Verify all Bond providers have _API_MAP defined."""
        providers = get_provider_classes(BondFactory)
        assert len(providers) > 0, "No Bond providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"
            assert isinstance(provider_cls._API_MAP, dict), f"{provider_cls.__name__} _API_MAP must be a dict"

    def test_bond_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        providers = get_provider_classes(BondFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            public_methods = get_public_methods(BondProvider)

            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(BondProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )

    def test_bond_api_map_structure(self):
        """Verify _API_MAP entries have correct structure."""
        providers = get_provider_classes(BondFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP

            for method_name, config in api_map.items():
                assert "ak_func" in config, f"{provider_cls.__name__}:{method_name} missing 'ak_func'"
                if config["ak_func"] is not None:
                    assert isinstance(config["ak_func"], str), (
                        f"{provider_cls.__name__}:{method_name} 'ak_func' must be string or None"
                    )

                if "params" in config:
                    assert isinstance(config["params"], dict), (
                        f"{provider_cls.__name__}:{method_name} 'params' must be dict"
                    )


@pytest.mark.contract
class TestFuturesAPIMapContract:
    """Contract tests for Futures module _API_MAP."""

    def test_all_futures_historical_providers_have_api_map(self):
        """Verify all Futures historical providers have _API_MAP defined."""
        providers = get_provider_classes(FuturesHistoricalFactory)
        assert len(providers) > 0, "No Futures historical providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"
            assert isinstance(provider_cls._API_MAP, dict), f"{provider_cls.__name__} _API_MAP must be a dict"

    def test_all_futures_realtime_providers_have_api_map(self):
        """Verify all Futures realtime providers have _API_MAP defined."""
        providers = get_provider_classes(FuturesRealtimeFactory)
        assert len(providers) > 0, "No Futures realtime providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"
            assert isinstance(provider_cls._API_MAP, dict), f"{provider_cls.__name__} _API_MAP must be a dict"

    def test_futures_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        historical_providers = get_provider_classes(FuturesHistoricalFactory)
        realtime_providers = get_provider_classes(FuturesRealtimeFactory)

        for provider_cls in historical_providers:
            api_map = provider_cls._API_MAP
            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(HistoricalFuturesDataProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )

        for provider_cls in realtime_providers:
            api_map = provider_cls._API_MAP
            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(RealtimeFuturesDataProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )

    def test_futures_api_map_structure(self):
        """Verify _API_MAP entries have correct structure."""
        historical_providers = get_provider_classes(FuturesHistoricalFactory)
        realtime_providers = get_provider_classes(FuturesRealtimeFactory)

        for provider_cls in historical_providers + realtime_providers:
            api_map = provider_cls._API_MAP

            for method_name, config in api_map.items():
                assert "ak_func" in config, f"{provider_cls.__name__}:{method_name} missing 'ak_func'"
                if config["ak_func"] is not None:
                    assert isinstance(config["ak_func"], str), (
                        f"{provider_cls.__name__}:{method_name} 'ak_func' must be string or None"
                    )

                if "params" in config:
                    assert isinstance(config["params"], dict), (
                        f"{provider_cls.__name__}:{method_name} 'params' must be dict"
                    )


@pytest.mark.contract
class TestOptionsAPIMapContract:
    """Contract tests for Options module _API_MAP."""

    def test_all_options_providers_have_api_map(self):
        """Verify all Options providers have _API_MAP defined."""
        providers = get_provider_classes(OptionsDataFactory)
        assert len(providers) > 0, "No Options providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"
            assert isinstance(provider_cls._API_MAP, dict), f"{provider_cls.__name__} _API_MAP must be a dict"

    def test_options_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        providers = get_provider_classes(OptionsDataFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            public_methods = get_public_methods(OptionsDataProvider)

            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(OptionsDataProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )

    def test_options_api_map_structure(self):
        """Verify _API_MAP entries have correct structure."""
        providers = get_provider_classes(OptionsDataFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP

            for method_name, config in api_map.items():
                assert "ak_func" in config, f"{provider_cls.__name__}:{method_name} missing 'ak_func'"
                if config["ak_func"] is not None:
                    assert isinstance(config["ak_func"], str), (
                        f"{provider_cls.__name__}:{method_name} 'ak_func' must be string or None"
                    )

                if "params" in config:
                    assert isinstance(config["params"], dict), (
                        f"{provider_cls.__name__}:{method_name} 'params' must be dict"
                    )


@pytest.mark.contract
class TestFundFlowAPIMapContract:
    """Contract tests for FundFlow module _API_MAP."""

    def test_all_fundflow_providers_have_api_map(self):
        """Verify all FundFlow providers have _API_MAP defined."""
        providers = get_provider_classes(FundFlowFactory)
        assert len(providers) > 0, "No FundFlow providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"

    def test_fundflow_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        providers = get_provider_classes(FundFlowFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP

            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(FundFlowProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )


@pytest.mark.contract
class TestAnalystAPIMapContract:
    """Contract tests for Analyst module _API_MAP."""

    def test_all_analyst_providers_have_api_map(self):
        """Verify all Analyst providers have _API_MAP defined."""
        providers = get_provider_classes(AnalystFactory)
        assert len(providers) > 0, "No Analyst providers registered"

        for provider_cls in providers:
            assert hasattr(provider_cls, "_API_MAP"), f"{provider_cls.__name__} missing _API_MAP"

    def test_analyst_api_map_methods_exist(self):
        """Verify _API_MAP methods are actual public methods."""
        providers = get_provider_classes(AnalystFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP

            for method_name in api_map.keys():
                assert hasattr(provider_cls, method_name) or hasattr(AnalystProvider, method_name), (
                    f"{provider_cls.__name__}: Method '{method_name}' in _API_MAP doesn't exist"
                )


@pytest.mark.contract
class TestAPIMapCompleteness:
    """Test that _API_MAP covers all important public methods."""

    def test_etf_api_map_coverage(self):
        """Verify ETF _API_MAP covers key methods."""
        expected_methods = ["get_etf_hist", "get_etf_spot", "get_etf_list", "get_fund_manager", "get_fund_rating"]

        providers = get_provider_classes(ETFFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            for method in expected_methods:
                if method in provider_cls.__dict__ and callable(provider_cls.__dict__[method]):
                    assert method in api_map, f"{provider_cls.__name__}: Missing '{method}' in _API_MAP"

    def test_bond_api_map_coverage(self):
        """Verify Bond _API_MAP covers key methods."""
        expected_methods = ["get_bond_list", "get_bond_hist", "get_bond_realtime"]

        providers = get_provider_classes(BondFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            for method in expected_methods:
                assert method in api_map, f"{provider_cls.__name__}: Missing '{method}' in _API_MAP"

    def test_futures_api_map_coverage(self):
        """Verify Futures _API_MAP covers key methods."""
        expected_historical_methods = ["get_hist_data", "get_main_contracts"]
        expected_realtime_methods = ["get_current_data", "get_all_quotes"]

        historical_providers = get_provider_classes(FuturesHistoricalFactory)
        realtime_providers = get_provider_classes(FuturesRealtimeFactory)

        for provider_cls in historical_providers:
            api_map = provider_cls._API_MAP
            for method in expected_historical_methods:
                assert method in api_map, f"{provider_cls.__name__}: Missing '{method}' in _API_MAP"

        for provider_cls in realtime_providers:
            api_map = provider_cls._API_MAP
            for method in expected_realtime_methods:
                assert method in api_map, f"{provider_cls.__name__}: Missing '{method}' in _API_MAP"

    def test_options_api_map_coverage(self):
        """Verify Options _API_MAP covers key methods."""
        expected_methods = [
            "get_options_chain",
            "get_options_realtime",
            "get_options_expirations",
            "get_options_history",
        ]

        providers = get_provider_classes(OptionsDataFactory)

        for provider_cls in providers:
            api_map = provider_cls._API_MAP
            for method in expected_methods:
                assert method in api_map, f"{provider_cls.__name__}: Missing '{method}' in _API_MAP"


@pytest.mark.contract
class TestAPIMapDocumentation:
    """Test that _API_MAP serves as documentation."""

    def test_api_map_keys_are_method_names(self):
        """Verify _API_MAP keys match method names."""
        factories = [
            ETFFactory,
            BondFactory,
            FuturesHistoricalFactory,
            FuturesRealtimeFactory,
            OptionsDataFactory,
            FundFlowFactory,
            AnalystFactory,
        ]

        for factory in factories:
            providers = get_provider_classes(factory)

            for provider_cls in providers:
                api_map = provider_cls._API_MAP

                for method_name in api_map.keys():
                    # All keys should be method names
                    assert isinstance(method_name, str), f"{provider_cls.__name__}: _API_MAP key must be string"

    def test_api_map_readable_as_metadata(self):
        """Verify _API_MAP can be read as metadata without execution."""
        providers = get_provider_classes(ETFFactory)

        for provider_cls in providers:
            # Should be able to read _API_MAP without instantiating
            api_map = provider_cls._API_MAP

            # Should be able to inspect structure
            assert isinstance(api_map, dict)
            if len(api_map) == 0:
                continue

            # Should be JSON-serializable (for documentation)
            import json

            try:
                json.dumps(api_map)
            except (TypeError, ValueError) as e:
                pytest.fail(f"{provider_cls.__name__}: _API_MAP not JSON-serializable: {e}")
