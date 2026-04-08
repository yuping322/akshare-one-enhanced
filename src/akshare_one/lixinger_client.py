"""
Lixinger API client for making requests to Lixinger OpenAPI.

This module provides a singleton client for managing Lixinger API connections,
token management, and request handling.
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


class LixingerClient:
    """Lixinger API client with token management and retry mechanism.

    This is a singleton client that manages:
    - Token authentication (from env var or config file)
    - HTTP session with retry strategy
    - API request/response handling
    """

    _instance: ClassVar["LixingerClient | None"] = None
    BASE_URL = "https://open.lixinger.com/api/"

    def __new__(cls) -> "LixingerClient":
        if cls._instance is None:
            instance = super().__new__(cls)
            object.__setattr__(instance, "_token", cls._load_token())
            object.__setattr__(instance, "_session", cls._create_session())
            object.__setattr__(instance, "logger", get_logger(__name__))
            cls._instance = instance
        return cls._instance

    @classmethod
    def _load_token(cls) -> str:
        """Load token from environment or config file.

        Priority:
        1. LIXINGER_TOKEN environment variable
        2. token.cfg in project root (where .git exists)
        3. token.cfg in current directory

        Returns:
            str: Token or empty string if not found
        """
        token = os.getenv("LIXINGER_TOKEN")
        if token:
            return token

        def read_token_file(cfg_path: Path) -> str:
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        if content.startswith("["):
                            import configparser

                            config = configparser.ConfigParser()
                            config.read_string(content)
                            return config.get("lixinger", "token", fallback="")
                        return content
            except Exception:
                pass
            return ""

        curr_dir = Path(os.getcwd()).resolve()

        root_dir = curr_dir
        while root_dir.parent != root_dir:
            if (root_dir / ".git").exists():
                cfg_path = root_dir / "token.cfg"
                if cfg_path.exists():
                    token = read_token_file(cfg_path)
                    if token:
                        return token
                break
            root_dir = root_dir.parent

        cfg_path = curr_dir / "token.cfg"
        if cfg_path.exists():
            token = read_token_file(cfg_path)
            if token:
                return token

        return ""

    @classmethod
    def _create_session(cls) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def query_api(self, api_suffix: str, params: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
        """Query Lixinger API.

        Args:
            api_suffix: API suffix (e.g., 'cn/company' or 'cn.company')
            params: Query parameters (without token)
            timeout: Request timeout in seconds

        Returns:
            dict: API response

        Raises:
            RuntimeError: If token not configured or request fails
        """
        if not self._token:
            raise RuntimeError("Lixinger token not configured. Please set LIXINGER_TOKEN or create token.cfg")

        params["token"] = self._token
        headers = {"Content-Type": "application/json"}

        suffix = api_suffix.replace(".", "/")
        if suffix.startswith("/"):
            suffix = suffix[1:]
        url = self.BASE_URL + suffix

        start_time = time.time()

        try:
            response = self._session.post(url=url, data=json.dumps(params), headers=headers, timeout=timeout)

            duration_ms = (time.time() - start_time) * 1000
            result = response.json()

            if result.get("code") == 1:
                self.logger.info(
                    f"API request successful: {api_suffix}",
                    extra={
                        "context": {
                            "log_type": "api_request",
                            "provider": "lixinger",
                            "api_suffix": api_suffix,
                            "duration_ms": round(duration_ms, 2),
                            "status": "success",
                        }
                    },
                )
            else:
                self.logger.warning(
                    f"API returned error: {api_suffix}",
                    extra={
                        "context": {
                            "log_type": "api_request",
                            "provider": "lixinger",
                            "api_suffix": api_suffix,
                            "duration_ms": round(duration_ms, 2),
                            "status": "error",
                            "error_msg": result.get("msg"),
                            "error_code": result.get("code"),
                        }
                    },
                )

            return result

        except requests.exceptions.Timeout:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"API request timeout: {api_suffix}",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "provider": "lixinger",
                        "api_suffix": api_suffix,
                        "duration_ms": round(duration_ms, 2),
                        "status": "timeout",
                    }
                },
            )
            raise RuntimeError(f"API request timeout after {timeout}s")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"API request failed: {api_suffix}",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "provider": "lixinger",
                        "api_suffix": api_suffix,
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
    def token(self) -> str:
        """Get the configured token."""
        return self._token

    @property
    def session(self) -> requests.Session:
        """Get the HTTP session."""
        return self._session


def get_lixinger_client() -> LixingerClient:
    """Get the singleton Lixinger client instance."""
    return LixingerClient()
