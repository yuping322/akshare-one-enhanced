"""
Unit tests for FieldMappingConfig module.

Tests cover:
- Default configuration loading
- Configuration file loading
- Configuration validation
- Configuration override
- Missing configuration key handling
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from akshare_one.modules.config import (
    FieldMappingConfig,
    get_field_mapping_config,
    get_module_amount_fields,
    get_module_field_types,
)
from akshare_one.modules.field_naming import FieldType


class TestConfigLoadDefault:
    """Test default configuration loading"""

    def test_singleton_pattern(self):
        """Test that FieldMappingConfig follows singleton pattern"""
        config1 = FieldMappingConfig()
        config2 = FieldMappingConfig()

        assert config1 is config2
        assert FieldMappingConfig._instance is config1

    def test_get_field_mapping_config_returns_singleton(self):
        """Test get_field_mapping_config returns singleton instance"""
        config1 = get_field_mapping_config()
        config2 = get_field_mapping_config()

        assert config1 is config2
        assert isinstance(config1, FieldMappingConfig)

    def test_default_config_has_version(self):
        """Test that default config has version field"""
        config = FieldMappingConfig()

        assert hasattr(config, "_config")
        assert "version" in config._config
        assert config._config["version"] == "1.0"

    def test_default_config_has_modules(self):
        """Test that default config has modules field"""
        config = FieldMappingConfig()

        assert "modules" in config._config
        assert isinstance(config._config["modules"], dict)

    def test_get_all_modules_returns_list(self):
        """Test get_all_modules returns list of module names"""
        config = FieldMappingConfig()
        modules = config.get_all_modules()

        assert isinstance(modules, list)
        assert "fundflow" in modules
        assert "northbound" in modules


class TestConfigLoadFromFile:
    """Test loading configuration from file"""

    def test_load_config_from_existing_file(self):
        """Test loading configuration from existing JSON file"""
        config = FieldMappingConfig()

        assert config._config is not None
        assert "modules" in config._config
        assert len(config._config["modules"]) > 0

    def test_load_config_with_valid_json(self):
        """Test that valid JSON is loaded correctly"""
        config = FieldMappingConfig()

        assert "fundflow" in config._config["modules"]
        fundflow_config = config._config["modules"]["fundflow"]
        assert "field_types" in fundflow_config
        assert "amount_fields" in fundflow_config

    def test_load_config_file_not_exists(self):
        """Test behavior when config file does not exist"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            original_instance = FieldMappingConfig._instance
            FieldMappingConfig._instance = None

            try:
                config = FieldMappingConfig()
                assert config._config == {"version": "1.0", "modules": {}}
            finally:
                FieldMappingConfig._instance = original_instance

    def test_reload_config(self):
        """Test reload configuration"""
        config = FieldMappingConfig()
        original_modules = config.get_all_modules()

        config.reload()

        reloaded_modules = config.get_all_modules()
        assert isinstance(reloaded_modules, list)


class TestConfigValidation:
    """Test configuration validation"""

    def test_get_module_config_valid_module(self):
        """Test getting config for valid module"""
        config = FieldMappingConfig()
        module_config = config.get_module_config("fundflow")

        assert isinstance(module_config, dict)
        assert "field_types" in module_config
        assert "amount_fields" in module_config

    def test_get_module_config_invalid_module(self):
        """Test getting config for invalid module returns empty dict"""
        config = FieldMappingConfig()
        module_config = config.get_module_config("nonexistent_module")

        assert module_config == {}

    def test_get_field_types_valid_module(self):
        """Test getting field types for valid module"""
        config = FieldMappingConfig()
        field_types = config.get_field_types("fundflow")

        assert isinstance(field_types, dict)
        assert "date" in field_types
        assert field_types["date"] == FieldType.DATE
        assert "symbol" in field_types
        assert field_types["symbol"] == FieldType.SYMBOL

    def test_get_field_types_invalid_module(self):
        """Test getting field types for invalid module returns empty dict"""
        config = FieldMappingConfig()
        field_types = config.get_field_types("nonexistent_module")

        assert field_types == {}

    def test_get_field_types_invalid_field_type_string(self):
        """Test handling invalid field type string in config"""
        config = FieldMappingConfig()

        with patch.object(config, "get_module_config") as mock_get:
            mock_get.return_value = {"field_types": {"valid_field": "DATE", "invalid_field": "INVALID_TYPE"}}

            field_types = config.get_field_types("test_module")

            assert "valid_field" in field_types
            assert field_types["valid_field"] == FieldType.DATE
            assert "invalid_field" not in field_types


class TestConfigOverride:
    """Test configuration override behavior"""

    def test_module_config_override_field_types(self):
        """Test that module config properly returns field_types"""
        config = FieldMappingConfig()
        fundflow_config = config.get_module_config("fundflow")

        assert "field_types" in fundflow_config
        field_types = fundflow_config["field_types"]

        assert isinstance(field_types, dict)
        assert "date" in field_types
        assert field_types["date"] == "DATE"

    def test_module_config_override_amount_fields(self):
        """Test that module config properly returns amount_fields"""
        config = FieldMappingConfig()
        northbound_config = config.get_module_config("northbound")

        assert "amount_fields" in northbound_config
        amount_fields = northbound_config["amount_fields"]

        assert isinstance(amount_fields, dict)
        assert "net_buy" in amount_fields
        assert amount_fields["net_buy"] == "yi_yuan"

    def test_get_amount_fields_valid_module(self):
        """Test getting amount fields for valid module"""
        config = FieldMappingConfig()
        amount_fields = config.get_amount_fields("fundflow")

        assert isinstance(amount_fields, dict)
        assert "fundflow_main_net_inflow" in amount_fields
        assert amount_fields["fundflow_main_net_inflow"] == "yuan"

    def test_get_amount_fields_invalid_module(self):
        """Test getting amount fields for invalid module returns empty dict"""
        config = FieldMappingConfig()
        amount_fields = config.get_amount_fields("nonexistent_module")

        assert amount_fields == {}

    def test_module_config_structure(self):
        """Test module config has expected structure"""
        config = FieldMappingConfig()

        for module_name in ["fundflow", "northbound", "margin"]:
            module_config = config.get_module_config(module_name)
            assert "field_types" in module_config or "amount_fields" in module_config


class TestConfigMissingKey:
    """Test handling of missing configuration keys"""

    def test_get_module_config_missing_key(self):
        """Test getting module config for missing module"""
        config = FieldMappingConfig()

        result = config.get_module_config("totally_nonexistent_module_xyz")
        assert result == {}

    def test_get_field_types_missing_module(self):
        """Test getting field types for missing module"""
        config = FieldMappingConfig()

        result = config.get_field_types("totally_nonexistent_module_xyz")
        assert result == {}

    def test_get_amount_fields_missing_module(self):
        """Test getting amount fields for missing module"""
        config = FieldMappingConfig()

        result = config.get_amount_fields("totally_nonexistent_module_xyz")
        assert result == {}

    def test_get_field_types_empty_field_types(self):
        """Test getting field types when field_types is empty"""
        config = FieldMappingConfig()

        with patch.object(config, "get_module_config") as mock_get:
            mock_get.return_value = {"amount_fields": {}}

            result = config.get_field_types("test_module")
            assert result == {}

    def test_get_amount_fields_empty_amount_fields(self):
        """Test getting amount fields when amount_fields is empty"""
        config = FieldMappingConfig()

        with patch.object(config, "get_module_config") as mock_get:
            mock_get.return_value = {"field_types": {}}

            result = config.get_amount_fields("test_module")
            assert result == {}


class TestModuleFunctions:
    """Test module-level convenience functions"""

    def test_get_module_field_types(self):
        """Test get_module_field_types convenience function"""
        field_types = get_module_field_types("fundflow")

        assert isinstance(field_types, dict)
        assert "date" in field_types
        assert field_types["date"] == FieldType.DATE

    def test_get_module_amount_fields(self):
        """Test get_module_amount_fields convenience function"""
        amount_fields = get_module_amount_fields("northbound")

        assert isinstance(amount_fields, dict)
        assert "net_buy" in amount_fields

    def test_get_module_field_types_nonexistent_module(self):
        """Test get_module_field_types with nonexistent module"""
        field_types = get_module_field_types("nonexistent_module")
        assert field_types == {}

    def test_get_module_amount_fields_nonexistent_module(self):
        """Test get_module_amount_fields with nonexistent module"""
        amount_fields = get_module_amount_fields("nonexistent_module")
        assert amount_fields == {}


class TestConfigSingletonReset:
    """Test singleton pattern behavior"""

    def test_singleton_persists_across_multiple_calls(self):
        """Test that singleton persists across multiple calls"""
        FieldMappingConfig._instance = None

        config1 = FieldMappingConfig()
        config2 = FieldMappingConfig()
        config3 = get_field_mapping_config()

        assert config1 is config2
        assert config2 is config3

    def test_reload_preserves_singleton(self):
        """Test that reload preserves singleton instance"""
        config = FieldMappingConfig()
        original_id = id(config)

        config.reload()

        assert id(config) == original_id
        assert FieldMappingConfig._instance is config


class TestMultipleModules:
    """Test configuration for multiple modules"""

    def test_all_modules_have_required_structure(self):
        """Test that all modules have required configuration structure"""
        config = FieldMappingConfig()
        modules = config.get_all_modules()

        for module_name in modules:
            module_config = config.get_module_config(module_name)

            assert isinstance(module_config, dict)

    def test_field_types_are_valid_enum_values(self):
        """Test that all field types in config are valid enum values"""
        config = FieldMappingConfig()
        modules = config.get_all_modules()

        valid_types = {ft.name for ft in FieldType}

        for module_name in modules:
            module_config = config.get_module_config(module_name)
            field_types_raw = module_config.get("field_types", {})

            for field_name, type_str in field_types_raw.items():
                assert type_str in valid_types, (
                    f"Invalid type '{type_str}' for field '{field_name}' in module '{module_name}'"
                )

    def test_amount_fields_have_valid_units(self):
        """Test that all amount fields have valid unit values"""
        config = FieldMappingConfig()
        modules = config.get_all_modules()

        valid_units = {"yuan", "wan_yuan", "yi_yuan"}

        for module_name in modules:
            module_config = config.get_module_config(module_name)
            amount_fields = module_config.get("amount_fields", {})

            for field_name, unit in amount_fields.items():
                assert unit in valid_units, f"Invalid unit '{unit}' for field '{field_name}' in module '{module_name}'"

    def test_get_field_types_multiple_modules(self):
        """Test getting field types for multiple modules"""
        config = FieldMappingConfig()

        fundflow_types = config.get_field_types("fundflow")
        northbound_types = config.get_field_types("northbound")
        margin_types = config.get_field_types("margin")

        assert len(fundflow_types) > 0
        assert len(northbound_types) > 0
        assert len(margin_types) > 0

        assert all(isinstance(ft, FieldType) for ft in fundflow_types.values())
        assert all(isinstance(ft, FieldType) for ft in northbound_types.values())
        assert all(isinstance(ft, FieldType) for ft in margin_types.values())


class TestConfigEdgeCases:
    """Test edge cases and error handling"""

    def test_get_module_config_empty_module_name(self):
        """Test getting config with empty module name"""
        config = FieldMappingConfig()

        result = config.get_module_config("")
        assert result == {}

    def test_get_field_types_empty_module_name(self):
        """Test getting field types with empty module name"""
        config = FieldMappingConfig()

        result = config.get_field_types("")
        assert result == {}

    def test_get_amount_fields_empty_module_name(self):
        """Test getting amount fields with empty module name"""
        config = FieldMappingConfig()

        result = config.get_amount_fields("")
        assert result == {}

    def test_module_config_with_nested_access(self):
        """Test nested access to module config"""
        config = FieldMappingConfig()

        field_types = config.get_field_types("fundflow")
        assert isinstance(field_types, dict)

        if "date" in field_types:
            assert field_types["date"] == FieldType.DATE

    def test_config_handles_unicode_module_name(self):
        """Test config handles unicode module names"""
        config = FieldMappingConfig()

        result = config.get_module_config("测试模块")
        assert result == {}

    def test_get_field_types_converts_enum_correctly(self):
        """Test that field type strings are correctly converted to enum"""
        config = FieldMappingConfig()
        field_types = config.get_field_types("fundflow")

        for field_name, field_type in field_types.items():
            assert isinstance(field_type, FieldType)
