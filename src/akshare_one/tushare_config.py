"""
Tushare Pro configuration management.

This module provides configuration management for Tushare Pro API access.
"""

import os
from typing import Optional


class TushareConfig:
    """Tushare Pro configuration manager."""

    _instance: Optional["TushareConfig"] = None
    _api_key: Optional[str] = None

    def __new__(cls) -> "TushareConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from environment variables or config files."""
        self._api_key = os.getenv("TUSHARE_API_KEY")

    def set_api_key(self, api_key: str) -> None:
        """Set API key manually."""
        self._api_key = api_key

    def get_api_key(self) -> Optional[str]:
        """Get the current API key."""
        return self._api_key

    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return self._api_key is not None and len(self._api_key) > 0

    def clear_api_key(self) -> None:
        """Clear the API key."""
        self._api_key = None


def get_tushare_config() -> TushareConfig:
    """Get the singleton TushareConfig instance."""
    return TushareConfig()


def set_tushare_api_key(api_key: str) -> None:
    """Set Tushare API key globally."""
    get_tushare_config().set_api_key(api_key)


def get_tushare_api_key() -> Optional[str]:
    """Get the current Tushare API key."""
    return get_tushare_config().get_api_key()


def has_tushare_api_key() -> bool:
    """Check if Tushare API key is configured."""
    return get_tushare_config().has_api_key()
