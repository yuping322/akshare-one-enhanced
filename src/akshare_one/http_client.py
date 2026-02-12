"""HTTP client with SSL configuration options."""

import os
import warnings
from typing import Any, ClassVar

import requests


class HttpClient:
    """HTTP client with configurable SSL verification.

    This client allows disabling SSL verification for environments with
    certificate issues, while maintaining security by default.
    """

    _instance: ClassVar["HttpClient | None"] = None
    _verify_ssl: ClassVar[bool] = True

    def __new__(cls) -> "HttpClient":
        if cls._instance is None:
            instance = super().__new__(cls)
            object.__setattr__(instance, "_session", requests.Session())
            instance._update_verify_setting()
            cls._instance = instance
        return cls._instance

    @classmethod
    def set_verify_ssl(cls, verify: bool) -> None:
        """Set SSL verification globally.

        Args:
            verify: Whether to verify SSL certificates
        """
        cls._verify_ssl = verify
        if cls._instance is not None:
            cls._instance._update_verify_setting()

    @classmethod
    def get_verify_ssl(cls) -> bool:
        """Get current SSL verification setting."""
        return cls._verify_ssl

    def _update_verify_setting(self) -> None:
        """Update session verify setting."""
        self._session.verify = self._verify_ssl

    @property
    def session(self) -> requests.Session:
        """Get the configured requests session."""
        return self._session

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a GET request."""
        return self._session.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a POST request."""
        return self._session.post(url, **kwargs)


def get_http_client() -> HttpClient:
    """Get the singleton HTTP client instance."""
    return HttpClient()


def configure_ssl_verification(verify: bool | None = None) -> bool:
    """Configure SSL verification based on parameter or environment variable.

    Priority:
    1. Function parameter if provided
    2. AKSHARE_ONE_VERIFY_SSL environment variable
    3. Default to True (secure)

    Args:
        verify: Explicit setting, or None to use environment/config

    Returns:
        The effective verify setting
    """
    if verify is not None:
        HttpClient.set_verify_ssl(verify)
        return verify

    # Check environment variable
    env_verify = os.environ.get("AKSHARE_ONE_VERIFY_SSL", "true").lower()
    verify_setting = env_verify not in ("false", "0", "no", "off")

    HttpClient.set_verify_ssl(verify_setting)

    if not verify_setting:
        warnings.warn(
            (
                "SSL verification is disabled. This is insecure and should only "
                "be used in development environments."
            ),
            SecurityWarning,
            stacklevel=2,
        )

    return verify_setting


class SecurityWarning(UserWarning):
    """Warning for security-related issues."""
    pass
