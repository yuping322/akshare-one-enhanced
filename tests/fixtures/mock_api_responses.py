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


@pytest.fixture
def mock_northbound_flow_api(mocker):
    """
    Mock akshare.stock_hsgt_hist_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_hsgt_hist_em',
        return_value=get_mock_northbound_flow_data()
    )


@pytest.fixture
def mock_northbound_holdings_individual_api(mocker):
    """
    Mock akshare.stock_hsgt_individual_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_hsgt_individual_em',
        return_value=get_mock_northbound_holdings_individual_data()
    )


@pytest.fixture
def mock_northbound_holdings_all_api(mocker):
    """
    Mock akshare.stock_hsgt_hold_stock_em API call.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_hsgt_hold_stock_em',
        return_value=get_mock_northbound_holdings_all_data()
    )


@pytest.fixture
def mock_northbound_top_stocks_api(mocker):
    """
    Mock akshare.stock_hsgt_hold_stock_em API call for top stocks.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_hsgt_hold_stock_em',
        return_value=get_mock_northbound_top_stocks_data()
    )


@pytest.fixture
def mock_block_deal_api(mocker):
    """
    Mock block deal API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_block_trade',
        return_value=get_mock_block_deal_data()
    )


@pytest.fixture
def mock_stock_fund_flow_api(mocker):
    """
    Mock stock fund flow API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_individual_fund_flow',
        return_value=get_mock_stock_fund_flow_data()
    )


@pytest.fixture
def mock_sector_fund_flow_api(mocker):
    """
    Mock sector fund flow API calls.

    Args:
        mocker: pytest-mock mocker fixture

    Returns:
        Mock object for the API call
    """
    return mocker.patch(
        'akshare.stock_sector_fund_flow',
        return_value=get_mock_sector_fund_flow_data()
    )


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
        'stock_hsgt_hist_em': mocker.patch(
            'akshare.stock_hsgt_hist_em',
            return_value=get_mock_northbound_flow_data()
        ),
        'stock_hsgt_individual_em': mocker.patch(
            'akshare.stock_hsgt_individual_em',
            return_value=get_mock_northbound_holdings_individual_data()
        ),
        'stock_hsgt_hold_stock_em': mocker.patch(
            'akshare.stock_hsgt_hold_stock_em',
            return_value=get_mock_northbound_holdings_all_data()
        ),
        'stock_block_trade': mocker.patch(
            'akshare.stock_block_trade',
            return_value=get_mock_block_deal_data()
        ),
        'stock_individual_fund_flow': mocker.patch(
            'akshare.stock_individual_fund_flow',
            return_value=get_mock_stock_fund_flow_data()
        ),
        'stock_sector_fund_flow': mocker.patch(
            'akshare.stock_sector_fund_flow',
            return_value=get_mock_sector_fund_flow_data()
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
    return mocker.patch('akshare.stock_hsgt_hist_em', return_value=empty_df)


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
    return mocker.patch(
        'akshare.stock_hsgt_hist_em',
        side_effect=ConnectionError("Network error")
    )


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
            mocks[api_name] = mocker.patch(f'akshare.{api_name}', return_value=data)
        return mocks


@pytest.fixture
def mock_api_response():
    """
    Fixture providing MockAPIResponse helper class.

    Returns:
        MockAPIResponse: Helper for creating custom mock responses
    """
    return MockAPIResponse()