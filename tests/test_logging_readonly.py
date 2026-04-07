"""
Test logging behavior in read-only/restricted environments.

This test verifies that:
1. get_logger() works even when log directory is not writable
2. setup_logging() with enable_file=True gracefully degrades when log creation fails
3. Provider initialization is not blocked by logging failures
"""

import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.akshare_one.logging_config import get_logger, setup_logging


class TestLoggingReadOnlyEnvironment(unittest.TestCase):
    """Test logging in read-only environments."""

    def setUp(self):
        """Clear existing handlers before each test."""
        root_logger = logging.getLogger("akshare_one")
        root_logger.handlers = []
        root_logger.filters = []

    def tearDown(self):
        """Clean up after each test."""
        root_logger = logging.getLogger("akshare_one")
        root_logger.handlers = []
        root_logger.filters = []

    def test_setup_logging_default_no_file(self):
        """Test that setup_logging() defaults to enable_file=False."""
        logger = setup_logging()

        # Should have only console handler, not file handler
        root_logger = logging.getLogger("akshare_one")
        handler_types = [type(h).__name__ for h in root_logger.handlers]

        self.assertIn("StreamHandler", handler_types)
        self.assertNotIn("TimedRotatingFileHandler", handler_types)

    def test_setup_logging_with_unwritable_directory(self):
        """Test that setup_logging() gracefully degrades when log directory is not writable."""
        # Use a non-existent or unwritable path
        unwritable_path = "/nonexistent/logs"

        # Should emit warning but not crash
        with self.assertWarns(RuntimeWarning):
            logger = setup_logging(
                log_dir=unwritable_path,
                enable_file=True,
            )

        # Should have console handler as fallback
        root_logger = logging.getLogger("akshare_one")
        handler_types = [type(h).__name__ for h in root_logger.handlers]

        self.assertIn("StreamHandler", handler_types)

    def test_get_logger_always_returns_logger(self):
        """Test that get_logger() always returns a usable logger."""
        # Clear handlers
        logging.getLogger("akshare_one").handlers = []

        logger = get_logger("test_module")

        # Should return a logger
        self.assertIsInstance(logger, logging.Logger)
        self.assertTrue(logger.name.startswith("akshare_one"))

        # Root logger should have handlers now
        root_logger = logging.getLogger("akshare_one")
        self.assertTrue(len(root_logger.handlers) > 0)

    def test_get_logger_with_failed_setup(self):
        """Test that get_logger() handles setup failures gracefully."""
        # Clear handlers
        logging.getLogger("akshare_one").handlers = []

        # Mock setup_logging to raise an exception
        with patch("src.akshare_one.logging_config.setup_logging", side_effect=Exception("Mock failure")):
            logger = get_logger("test_module")

        # Should still return a logger with fallback handler
        self.assertIsInstance(logger, logging.Logger)
        root_logger = logging.getLogger("akshare_one")
        self.assertTrue(len(root_logger.handlers) > 0)

    def test_provider_initialization_in_readonly_env(self):
        """Test that providers can be initialized in read-only environments."""
        from src.akshare_one.modules.realtime.eastmoney import EastmoneyRealtimeProvider

        # Clear handlers
        logging.getLogger("akshare_one").handlers = []

        # Try to initialize provider with unwritable log directory
        with patch.dict(os.environ, {"AKSHARE_ONE_LOG_DIR": "/nonexistent/logs"}):
            # Provider should initialize successfully
            provider = EastmoneyRealtimeProvider(symbol="600000")

            self.assertIsNotNone(provider)
            self.assertEqual(provider.symbol, "600000")
            self.assertIsNotNone(provider.logger)

    def test_logger_works_after_graceful_degradation(self):
        """Test that logger actually works after graceful degradation."""
        # Clear handlers
        logging.getLogger("akshare_one").handlers = []

        # Setup with unwritable directory
        with self.assertWarns(RuntimeWarning):
            logger = setup_logging(
                log_dir="/nonexistent/path",
                enable_file=True,
            )

        # Logger should still work
        with self.assertLogs("akshare_one", level="INFO"):
            logger.info("Test message after degradation")

    def test_temp_readonly_directory(self):
        """Test with actual read-only directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory and make it read-only
            readonly_dir = Path(tmpdir) / "readonly_logs"
            readonly_dir.mkdir()

            # Try to make it read-only (may not work on all systems)
            try:
                os.chmod(readonly_dir, 0o444)

                # Attempt setup_logging with this directory
                try:
                    with self.assertWarns(RuntimeWarning):
                        logger = setup_logging(
                            log_dir=str(readonly_dir),
                            enable_file=True,
                        )
                except PermissionError:
                    # If permission check fails, should still have console handler
                    root_logger = logging.getLogger("akshare_one")
                    handler_types = [type(h).__name__ for h in root_logger.handlers]
                    self.assertIn("StreamHandler", handler_types)

                # Logger should work
                self.assertIsNotNone(logger)

            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(readonly_dir, 0o755)
                except OSError:
                    pass


if __name__ == "__main__":
    unittest.main()