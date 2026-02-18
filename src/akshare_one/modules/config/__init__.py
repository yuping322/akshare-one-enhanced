"""
Field mapping configuration loader.

This module provides utilities to load and manage field mapping configurations.
"""

import contextlib
import json
import os
from typing import Any, Optional

from ..field_naming import FieldType


class FieldMappingConfig:
    """Field mapping configuration manager."""

    _instance: Optional["FieldMappingConfig"] = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> "FieldMappingConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from file."""
        config_path = os.path.join(os.path.dirname(__file__), "field_mappings.json")

        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            self._config = {"version": "1.0", "modules": {}}

    def get_module_config(self, module_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific module.

        Args:
            module_name: Name of the module (e.g., 'fundflow', 'northbound')

        Returns:
            Module configuration dictionary
        """
        return self._config.get("modules", {}).get(module_name, {})

    def get_field_types(self, module_name: str) -> dict[str, FieldType]:
        """
        Get field types for a specific module.

        Args:
            module_name: Name of the module

        Returns:
            Dictionary mapping field names to FieldType
        """
        module_config = self.get_module_config(module_name)
        field_types_raw = module_config.get("field_types", {})

        field_types = {}
        for field_name, type_str in field_types_raw.items():
            with contextlib.suppress(KeyError):
                field_types[field_name] = FieldType[type_str]

        return field_types

    def get_amount_fields(self, module_name: str) -> dict[str, str]:
        """
        Get amount fields with their units for a specific module.

        Args:
            module_name: Name of the module

        Returns:
            Dictionary mapping field names to their source units
        """
        module_config = self.get_module_config(module_name)
        return module_config.get("amount_fields", {})

    def get_all_modules(self) -> list[str]:
        """Get list of all configured modules."""
        return list(self._config.get("modules", {}).keys())

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


def get_field_mapping_config() -> FieldMappingConfig:
    """Get the singleton FieldMappingConfig instance."""
    return FieldMappingConfig()


def get_module_field_types(module_name: str) -> dict[str, FieldType]:
    """
    Get field types for a module.

    Args:
        module_name: Name of the module

    Returns:
        Dictionary mapping field names to FieldType
    """
    return get_field_mapping_config().get_field_types(module_name)


def get_module_amount_fields(module_name: str) -> dict[str, str]:
    """
    Get amount fields for a module.

    Args:
        module_name: Name of the module

    Returns:
        Dictionary mapping field names to their source units
    """
    return get_field_mapping_config().get_amount_fields(module_name)
