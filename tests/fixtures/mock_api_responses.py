"""
Mock API response fixtures for testing without network dependencies.

This module provides pytest fixtures that mock akshare API calls,
allowing tests to run offline without requiring network access.

Usage:
    @pytest.fixture
    def mock_akshare_api(mocker):
        '''Mock akshare API calls'''
        from tests.fixtures.northbound_fixtures import get_mock_northbound_flow_data
        mocker.patch('akshare.stock_hsgt_hist_em', return_value=get_mock_northbound_flow_data())
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock

from tests.fixtures.northbound_fixtures import (
    get_mock_northbound_flow_data,
    get_mock_northbound_holdings_individual_data,
    get_mock_northbound_holdings_all_data,
    get_mock_northbound_top_stocks_data,
)
from tests.fixtures.blockdeal_fixtures import (
    get_mock_block_deal_data,
    get_mock_block_deal_summary_data,
)
from tests.fixtures.fundflow_fixtures import (
    get_mock_stock_fund_flow_data,
    get_mock_sector_fund_flow_data,
    get_mock_industry_list_data,
    get_mock_concept_list_data,
)
from tests.fixtures.historical_fixtures import (
    get_mock_hist_data_daily,
    get_mock_hist_data_minute,
    get_mock_hist_data_hour,
    get_mock_hist_data_weekly,
    get_mock_hist_data_monthly,
    get_mock_hist_data_empty,
    get_mock_hist_data_with_nan,
    get_mock_hist_data_with_infinity,
    get_mock_hist_data_etf,
    get_mock_hist_data_extreme_values,
    get_mock_sina_daily_data,
    get_mock_sina_minute_data,
    get_mock_b_share_data,
)


@pytest.fixture
def mock_northbound_flow_api(mocker):
    """
    Mock akshare.stock_hsgt_hist_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_hsgt_hist_em", return_value=get_mock_northbound_flow_data())


@pytest.fixture
def mock_northbound_holdings_individual_api(mocker):
    """
    Mock akshare.stock_hsgt_individual_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_hsgt_individual_em", return_value=get_mock_northbound_holdings_individual_data())


@pytest.fixture
def mock_northbound_holdings_all_api(mocker):
    """
    Mock akshare.stock_hsgt_hold_stock_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_hsgt_hold_stock_em", return_value=get_mock_northbound_holdings_all_data())


@pytest.fixture
def mock_northbound_top_stocks_api(mocker):
    """
    Mock akshare.stock_hsgt_hold_stock_em API call for top stocks.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_hsgt_hold_stock_em", return_value=get_mock_northbound_top_stocks_data())


@pytest.fixture
def mock_block_deal_api(mocker):
    """
    Mock block deal API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    import akshare

    return mocker.patch.object(akshare, "stock_dzjy_mrtj", return_value=get_mock_block_deal_data())


@pytest.fixture
def mock_stock_fund_flow_api(mocker):
    """
    Mock stock fund flow API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_individual_fund_flow", return_value=get_mock_stock_fund_flow_data())


@pytest.fixture
def mock_sector_fund_flow_api(mocker):
    """
    Mock sector fund flow API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_sector_fund_flow", return_value=get_mock_sector_fund_flow_data())


@pytest.fixture
def mock_all_akshare_apis(mocker):
    """
    Mock all commonly used akshare APIs at once.

    This fixture provides a comprehensive mock setup for all APIs
    used in integration tests, allowing tests to run completely offline.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        dict: Dictionary of mock objects for all APIs
    """
    mocks = {
        "stock_hsgt_hist_em": mocker.patch("akshare.stock_hsgt_hist_em", return_value=get_mock_northbound_flow_data()),
        "stock_hsgt_individual_em": mocker.patch(
            "akshare.stock_hsgt_individual_em", return_value=get_mock_northbound_holdings_individual_data()
        ),
        "stock_hsgt_hold_stock_em": mocker.patch(
            "akshare.stock_hsgt_hold_stock_em", return_value=get_mock_northbound_holdings_all_data()
        ),
        "call_akshare": mocker.patch(
            "akshare_one.akshare_compat.call_akshare", return_value=get_mock_block_deal_data()
        ),
        "stock_individual_fund_flow": mocker.patch(
            "akshare.stock_individual_fund_flow", return_value=get_mock_stock_fund_flow_data()
        ),
        "stock_sector_fund_flow": mocker.patch(
            "akshare.stock_sector_fund_flow", return_value=get_mock_sector_fund_flow_data()
        ),
    }
    return mocks


@pytest.fixture
def empty_dataframe_mock(mocker):
    """
    Mock that returns empty DataFrame.

    Useful for testing edge cases where API returns no data.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that returns empty DataFrame
    """
    empty_df = pd.DataFrame()
    return mocker.patch("akshare.stock_hsgt_hist_em", return_value=empty_df)


@pytest.fixture
def api_error_mock(mocker):
    """
    Mock that raises exception to simulate API errors.

    Useful for testing error handling and fallback behavior.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that raises ConnectionError
    """
    return mocker.patch("akshare.stock_hsgt_hist_em", side_effect=ConnectionError("Network error"))


class MockAPIResponse:
    """
    Helper class for creating custom mock API responses.

    Usage:
        mock_response = MockAPIResponse()
        mock_response.add_data('stock_hsgt_hist_em', custom_data)
        mock_response.apply_mocks(mocker)
    """

    def __init__(self):
        self.mock_data = {}

    def add_data(self, api_name: str, data: pd.DataFrame):
        """
        Add custom mock data for an API.

        Args:
            api_name: Name of the akshare API function
            data: DataFrame to return
        """
        self.mock_data[api_name] = data

    def apply_mocks(self, mocker):
        """
        Apply all registered mocks.

        Args:
            mocker: pytest-mock mocker fixture

        Returns:
            dict: Dictionary of applied mock objects
        """
        mocks = {}
        for api_name, data in self.mock_data.items():
            mocks[api_name] = mocker.patch(f"akshare.{api_name}", return_value=data)
        return mocks


@pytest.fixture
def mock_api_response():
    """
    Fixture providing MockAPIResponse helper class.

    Returns:
        MockAPIResponse: Helper for creating custom mock responses
    """
    return MockAPIResponse()


@pytest.fixture
def mock_historical_eastmoney_api(mocker):
    """
    Mock eastmoney historical data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_daily()
    )


@pytest.fixture
def mock_historical_eastmoney_minute_api(mocker):
    """
    Mock eastmoney minute data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_minute()
    )


@pytest.fixture
def mock_historical_eastmoney_hour_api(mocker):
    """
    Mock eastmoney hourly data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_hour())


@pytest.fixture
def mock_historical_eastmoney_weekly_api(mocker):
    """
    Mock eastmoney weekly data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_weekly()
    )


@pytest.fixture
def mock_historical_eastmoney_monthly_api(mocker):
    """
    Mock eastmoney monthly data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_monthly()
    )


@pytest.fixture
def mock_historical_sina_api(mocker):
    """
    Mock Sina historical data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_zh_a_daily", return_value=get_mock_sina_daily_data())


@pytest.fixture
def mock_historical_sina_minute_api(mocker):
    """
    Mock Sina minute data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare.stock_zh_a_minute", return_value=get_mock_sina_minute_data())


@pytest.fixture
def mock_historical_empty_api(mocker):
    """
    Mock that returns empty DataFrame for historical data.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that returns empty DataFrame
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_empty()
    )


@pytest.fixture
def mock_historical_with_nan_api(mocker):
    """
    Mock that returns DataFrame with NaN values for historical data.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that returns DataFrame with NaN
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_with_nan()
    )


@pytest.fixture
def mock_historical_with_infinity_api(mocker):
    """
    Mock that returns DataFrame with Infinity values for historical data.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that returns DataFrame with Infinity
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_with_infinity()
    )


@pytest.fixture
def mock_historical_extreme_values_api(mocker):
    """
    Mock that returns DataFrame with extreme values for historical data.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that returns DataFrame with extreme values
    """
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_extreme_values()
    )


@pytest.fixture
def mock_historical_etf_api(mocker):
    """
    Mock ETF historical data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch("akshare_one.modules.historical.eastmoney.call_akshare", return_value=get_mock_hist_data_etf())


@pytest.fixture
def mock_historical_network_error(mocker):
    """
    Mock that raises network error for historical data API.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that raises ConnectionError
    """
    import requests

    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", side_effect=requests.ConnectionError("Network error")
    )


@pytest.fixture
def mock_historical_timeout_error(mocker):
    """
    Mock that raises timeout error for historical data API.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object that raises Timeout
    """
    import requests

    return mocker.patch(
        "akshare_one.modules.historical.eastmoney.call_akshare", side_effect=requests.Timeout("Timeout error")
    )


@pytest.fixture
def mock_realtime_data_api(mocker):
    """
    Mock realtime data API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.realtime.eastmoney_direct.EastMoneyDirectRealtime.get_current_data",
        return_value=get_mock_realtime_data(),
    )


@pytest.fixture
def mock_dragon_tiger_list_api(mocker):
    """
    Mock dragon tiger list API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.lhb.eastmoney.EastMoneyDragonTigerProvider.get_dragon_tiger_list",
        return_value=get_mock_dragon_tiger_list(),
    )


@pytest.fixture
def mock_financial_metrics_api(mocker):
    """
    Mock financial metrics API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        "akshare_one.modules.financial.eastmoney_direct.EastmoneyDirectFinancialProvider.get_financial_metrics",
        return_value=get_mock_financial_metrics(),
    )
