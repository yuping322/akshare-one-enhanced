"""
TickFlow API client for making requests to TickFlow行情数据 API.

This module provides a singleton client for managing TickFlow API connections,
API key management, and request handling.
"""

import os
import json
import time
from pathlib import Path
from typing import Any, ClassVar
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import get_logger


class TickFlowClient:
    """TickFlow API client with API key management and retry mechanism.

    This is a singleton client that manages:
    - API key authentication (from env var or config file)
    - HTTP session with retry strategy
    - API request/response handling
    """

    _instance: ClassVar["TickFlowClient | None"] = None
    BASE_URL = "https://api.tickflow.org"

    def __new__(cls) -> "TickFlowClient":
        if cls._instance is None:
            instance = super().__new__(cls)
            object.__setattr__(instance, "_api_key", cls._load_api_key())
            object.__setattr__(instance, "_session", cls._create_session())
            object.__setattr__(instance, "logger", get_logger(__name__))
            cls._instance = instance
        return cls._instance

    @classmethod
    def _load_api_key(cls) -> str:
        """Load API key from environment or config file.

        Priority:
        1. TICKFLOW_API_KEY environment variable
        2. tickflow.cfg in project root (where .git exists)
        3. tickflow.cfg in current directory

        Returns:
            str: API key or empty string if not found
        """
        api_key = os.getenv("TICKFLOW_API_KEY")
        if api_key:
            return api_key

        def read_config_file(cfg_path: Path) -> str:
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        if content.startswith("["):
                            import configparser

                            config = configparser.ConfigParser()
                            config.read_string(content)
                            return config.get("tickflow", "api_key", fallback="")
                        return content
            except Exception:
                pass
            return ""

        curr_dir = Path(os.getcwd()).resolve()

        root_dir = curr_dir
        while root_dir.parent != root_dir:
            if (root_dir / ".git").exists():
                cfg_path = root_dir / "tickflow.cfg"
                if cfg_path.exists():
                    api_key = read_config_file(cfg_path)
                    if api_key:
                        return api_key
                break
            root_dir = root_dir.parent

        cfg_path = curr_dir / "tickflow.cfg"
        if cfg_path.exists():
            api_key = read_config_file(cfg_path)
            if api_key:
                return api_key

        return ""

    @classmethod
    def _create_session(cls) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def query_api(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Query TickFlow API.

        Args:
            endpoint: API endpoint (e.g., '/v1/quotes')
            method: HTTP method (GET or POST)
            params: Query parameters for GET requests
            data: JSON body for POST requests
            timeout: Request timeout in seconds

        Returns:
            dict: API response

        Raises:
            RuntimeError: If API key not configured or request fails
        """
        if not self._api_key:
            raise RuntimeError("TickFlow API key not configured. Please set TICKFLOW_API_KEY or create tickflow.cfg")

        headers = {"Content-Type": "application/json", "x-api-key": self._api_key}

        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = self.BASE_URL + endpoint

        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = self._session.get(url, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = self._session.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            duration_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                self.logger.info(
                    f"API request successful: {endpoint}",
                    extra={
                        "context": {
                            "log_type": "api_request",
                            "provider": "tickflow",
                            "endpoint": endpoint,
                            "method": method,
                            "duration_ms": round(duration_ms, 2),
                            "status": "success",
                        }
                    },
                )
                return result
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", response.text)
                    error_code = error_data.get("code", "UNKNOWN_ERROR")
                except Exception:
                    error_msg = response.text
                    error_code = "UNKNOWN_ERROR"

                self.logger.error(
                    f"API returned error: {endpoint}",
                    extra={
                        "context": {
                            "log_type": "api_request",
                            "provider": "tickflow",
                            "endpoint": endpoint,
                            "method": method,
                            "duration_ms": round(duration_ms, 2),
                            "status": "error",
                            "error_msg": error_msg,
                            "error_code": error_code,
                            "status_code": response.status_code,
                        }
                    },
                )
                raise RuntimeError(f"API error ({response.status_code}): {error_msg}")

        except requests.exceptions.Timeout:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"API request timeout: {endpoint}",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "provider": "tickflow",
                        "endpoint": endpoint,
                        "method": method,
                        "duration_ms": round(duration_ms, 2),
                        "status": "timeout",
                    }
                },
            )
            raise RuntimeError(f"API request timeout after {timeout}s")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"API request failed: {endpoint}",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "provider": "tickflow",
                        "endpoint": endpoint,
                        "method": method,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_msg": str(e),
                    }
                },
                exc_info=True,
            )
            raise RuntimeError(f"API request failed: {e}")

    @property
    def api_key(self) -> str:
        """Get the configured API key."""
        return self._api_key

    @property
    def session(self) -> requests.Session:
        """Get the HTTP session."""
        return self._session


def get_tickflow_client() -> TickFlowClient:
    """Get the singleton TickFlow client instance."""
    return TickFlowClient()
