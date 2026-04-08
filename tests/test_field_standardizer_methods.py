"""
Unit tests for FieldStandardizer methods.

Tests the standardize_field_name, standardize_dataframe, and validate_field_name methods.
"""

import pandas as pd
import pytest

from akshare_one.modules.field_naming import (
    FieldStandardizer,
    FieldType,
    NamingRules,
)
from akshare_one.modules.field_naming.formatter import (
    FieldFormatter,
    StockCodeFormat,
    DateFormat,
    format_stock_code,
    format_date,
    format_float,
    format_int,
    format_boolean,
)
from akshare_one.modules.field_naming.field_mapper import FieldMapper
from akshare_one.modules.field_naming.alias_manager import FieldAliasManager
from akshare_one.modules.field_naming.field_validator import FieldValidator, ValidationResult
from akshare_one.modules.field_naming.models import FieldMapping, MappingConfig


class TestFieldFormattingRules:
    """测试字段格式化规则 - formatter.py"""

    def test_stock_code_pure_numeric_format(self):
        """测试纯数字股票代码格式"""
        result = FieldFormatter.normalize_stock_code("000001", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"

        result = FieldFormatter.normalize_stock_code("600000", StockCodeFormat.PURE_NUMERIC)
        assert result == "600000"

    def test_stock_code_with_suffix_format(self):
        """测试带后缀股票代码格式"""
        result = FieldFormatter.normalize_stock_code("000001.SZ", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"

        result = FieldFormatter.normalize_stock_code("sh600000", StockCodeFormat.WITH_SUFFIX)
        assert result == "600000.SH"

    def test_stock_code_with_prefix_format(self):
        """测试带前缀股票代码格式"""
        result = FieldFormatter.normalize_stock_code("sz000001", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"

        result = FieldFormatter.normalize_stock_code("000001.SZ", StockCodeFormat.WITH_PREFIX)
        assert result == "sz000001"

    def test_stock_code_market_inference(self):
        """测试股票代码市场推断"""
        result = FieldFormatter.normalize_stock_code("600000", StockCodeFormat.WITH_SUFFIX)
        assert ".SH" in result

        result = FieldFormatter.normalize_stock_code("000001", StockCodeFormat.WITH_SUFFIX)
        assert ".SZ" in result

        result = FieldFormatter.normalize_stock_code("430001", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result

    def test_date_format_yyyymmdd(self):
        """测试YYYYMMDD日期格式"""
        result = FieldFormatter.normalize_date("2024-01-01", DateFormat.YYYYMMDD)
        assert result == "20240101"

        result = FieldFormatter.normalize_date("20240101", DateFormat.YYYY_MM_DD)
        assert result == "2024-01-01"

    def test_date_format_chinese(self):
        """测试中文日期格式"""
        result = FieldFormatter.normalize_date("2024年1月1日", DateFormat.YYYY_MM_DD)
        assert result == "2024-01-01"

    def test_float_formatting_with_percent(self):
        """测试百分比浮点数格式化"""
        result = FieldFormatter.normalize_float("20.5%")
        assert result == 0.205

        result = FieldFormatter.normalize_float("100%")
        assert result == 1.0

    def test_float_formatting_with_comma(self):
        """测试带逗号浮点数格式化"""
        result = FieldFormatter.normalize_float("1,234.56")
        assert result == 1234.56

        result = FieldFormatter.normalize_float("1.234,56")
        assert result == 1.23456

    def test_int_formatting(self):
        """测试整数格式化"""
        result = FieldFormatter.normalize_int("123")
        assert result == 123

        result = FieldFormatter.normalize_int("45.6")
        assert result == 46

    def test_boolean_formatting(self):
        """测试布尔值格式化"""
        assert FieldFormatter.normalize_boolean("true") is True
        assert FieldFormatter.normalize_boolean("yes") is True
        assert FieldFormatter.normalize_boolean("是") is True
        assert FieldFormatter.normalize_boolean("false") is False
        assert FieldFormatter.normalize_boolean("no") is False
        assert FieldFormatter.normalize_boolean("否") is False


class TestFieldMappingConsistency:
    """测试字段映射一致性 - field_mapper.py"""

    def test_field_mapper_init(self):
        """测试字段映射器初始化"""
        mapper = FieldMapper(config_path=None)
        assert isinstance(mapper.mappings, dict)

    def test_field_mapper_map_fields(self):
        """测试字段映射应用"""
        mapper = FieldMapper()

        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="日期", standard_field="date", field_type=FieldType.DATE),
                FieldMapping(source_field="代码", standard_field="symbol", field_type=FieldType.SYMBOL),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        df = pd.DataFrame({"日期": ["2024-01-01", "2024-01-02"], "代码": ["000001", "000002"], "value": [100, 200]})

        result = mapper.map_fields(df, "test_source", "test_module")

        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "value" in result.columns

    def test_field_mapper_get_mapping(self):
        """测试获取特定字段映射"""
        mapper = FieldMapper()

        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="日期", standard_field="date", field_type=FieldType.DATE),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        mapping = mapper.get_mapping("test_source", "test_module", "日期")
        assert mapping is not None
        assert mapping.source_field == "日期"
        assert mapping.standard_field == "date"

    def test_field_mapper_add_mapping(self):
        """测试添加新映射"""
        mapper = FieldMapper()

        new_mapping = FieldMapping(source_field="成交额", standard_field="amount", field_type=FieldType.AMOUNT)

        mapper.add_mapping("test_source", "test_module", new_mapping)

        assert "test_source" in mapper.mappings
        assert "test_module" in mapper.mappings["test_source"]

    def test_field_mapper_no_config_returns_unchanged(self):
        """测试无配置时返回原DataFrame"""
        mapper = FieldMapper()

        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        result = mapper.map_fields(df, "nonexistent_source", "nonexistent_module")

        pd.testing.assert_frame_equal(result, df)


class TestAliasManagement:
    """测试别名管理 - alias_manager.py"""

    def test_alias_manager_init(self):
        """测试别名管理器初始化"""
        alias_config = {"old_field": "new_field", "legacy_name": "standard_name"}
        manager = FieldAliasManager(alias_config)

        assert manager.aliases == alias_config
        assert "new_field" in manager.reverse_aliases
        assert "old_field" in manager.reverse_aliases["new_field"]

    def test_alias_manager_add_aliases_to_dataframe(self):
        """测试为DataFrame添加别名"""
        alias_config = {"old_price": "price", "old_volume": "volume"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"price": [10.0, 20.0], "volume": [100, 200]})

        result = manager.add_aliases_to_dataframe(df)

        assert "old_price" in result.columns
        assert "old_volume" in result.columns
        assert result["old_price"].equals(result["price"])

    def test_alias_manager_resolve_field_access(self):
        """测试字段访问解析"""
        alias_config = {"deprecated_field": "current_field"}
        manager = FieldAliasManager(alias_config, enable_warnings=False)

        df = pd.DataFrame({"current_field": [1, 2, 3]})

        result = manager.resolve_field_access(df, "current_field")
        assert result.equals(df["current_field"])

        result = manager.resolve_field_access(df, "deprecated_field")
        assert result.equals(df["current_field"])

    def test_alias_manager_resolve_unknown_field_raises(self):
        """测试解析未知字段抛出异常"""
        alias_config = {"old_field": "new_field"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"other_field": [1, 2]})

        with pytest.raises(KeyError, match="not found"):
            manager.resolve_field_access(df, "unknown_field")

    def test_alias_manager_get_standard_name(self):
        """测试获取标准字段名"""
        alias_config = {"legacy_name": "standard_name"}
        manager = FieldAliasManager(alias_config)

        assert manager.get_standard_name("legacy_name") == "standard_name"
        assert manager.get_standard_name("unknown") is None

    def test_alias_manager_is_legacy_field(self):
        """测试检查是否为旧字段"""
        alias_config = {"old_field": "new_field"}
        manager = FieldAliasManager(alias_config)

        assert manager.is_legacy_field("old_field") is True
        assert manager.is_legacy_field("new_field") is False

    def test_alias_manager_add_alias(self):
        """测试添加新别名"""
        alias_config = {"old1": "new1"}
        manager = FieldAliasManager(alias_config)

        manager.add_alias("old2", "new2")

        assert "old2" in manager.aliases
        assert manager.aliases["old2"] == "new2"
        assert "old2" in manager.reverse_aliases["new2"]

    def test_alias_manager_remove_alias(self):
        """测试移除别名"""
        alias_config = {"old1": "new1", "old2": "new2"}
        manager = FieldAliasManager(alias_config)

        result = manager.remove_alias("old1")
        assert result is True
        assert "old1" not in manager.aliases

        result = manager.remove_alias("nonexistent")
        assert result is False


class TestFieldValidationRules:
    """测试字段验证规则 - field_validator.py"""

    def test_field_validator_init(self):
        """测试字段验证器初始化"""
        validator = FieldValidator()
        assert isinstance(validator.whitelist, set)
        assert isinstance(validator._field_type_patterns, dict)

    def test_field_validator_validate_dataframe(self):
        """测试DataFrame验证"""
        validator = FieldValidator()

        df = pd.DataFrame({"date": ["2024-01-01"], "symbol": ["000001"], "invalid_field": ["test"]})

        field_types = {"date": FieldType.DATE, "symbol": FieldType.SYMBOL}

        results = validator.validate_dataframe(df, field_types)

        assert "date" in results
        assert results["date"].is_valid is True
        assert "symbol" in results
        assert results["symbol"].is_valid is True

    def test_field_validator_whitelist(self):
        """测试白名单功能"""
        validator = FieldValidator(whitelist={"custom_field"})

        is_valid, error_msg, suggested = validator.validate_field_name("custom_field", FieldType.DATE)
        assert is_valid is True
        assert error_msg is None

    def test_field_validator_infer_field_type(self):
        """测试字段类型推断"""
        validator = FieldValidator()

        assert validator._infer_field_type("date") == FieldType.DATE
        assert validator._infer_field_type("timestamp") == FieldType.TIMESTAMP
        assert validator._infer_field_type("symbol") == FieldType.SYMBOL
        assert validator._infer_field_type("buy_amount") == FieldType.AMOUNT
        assert validator._infer_field_type("is_st") == FieldType.BOOLEAN

    def test_field_validator_generate_error_message(self):
        """测试错误消息生成"""
        validator = FieldValidator()

        error_msg = validator._generate_error_message("wrong_date", FieldType.DATE, r"^date$")

        assert "wrong_date" in error_msg
        assert "date" in error_msg.lower()

    def test_field_validator_generate_suggestion(self):
        """测试建议生成"""
        validator = FieldValidator()

        suggestion = validator._generate_suggestion("wrong_date", FieldType.DATE)
        assert suggestion == "date"

        suggestion = validator._generate_suggestion("amount_value", FieldType.AMOUNT)
        assert "_amount" in suggestion

    def test_field_validator_add_to_whitelist(self):
        """测试添加白名单"""
        validator = FieldValidator()

        validator.add_to_whitelist("approved_field")
        assert "approved_field" in validator.whitelist

    def test_field_validator_get_validation_summary(self):
        """测试验证摘要生成"""
        validator = FieldValidator()

        results = {
            "field1": ValidationResult(field_name="field1", is_valid=True, field_type=FieldType.DATE),
            "field2": ValidationResult(field_name="field2", is_valid=False, field_type=FieldType.SYMBOL),
        }

        summary = validator.get_validation_summary(results)

        assert summary["total_fields"] == 2
        assert summary["valid_fields"] == 1
        assert summary["invalid_fields"] == 1


class TestFieldNameNormalization:
    """测试字段名标准化"""

    def test_normalize_stock_code_short_code(self):
        """测试短代码补齐"""
        result = FieldFormatter.normalize_stock_code("1", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"

        result = FieldFormatter.normalize_stock_code("123", StockCodeFormat.PURE_NUMERIC)
        assert len(result) == 6

    def test_normalize_stock_code_none_input(self):
        """测试None输入"""
        result = FieldFormatter.normalize_stock_code(None, StockCodeFormat.PURE_NUMERIC)
        assert result is None

        result = FieldFormatter.normalize_stock_code("", StockCodeFormat.PURE_NUMERIC)
        assert result is None

    def test_normalize_date_none_input(self):
        """测试日期None输入"""
        result = FieldFormatter.normalize_date(None, DateFormat.YYYY_MM_DD)
        assert result is None

        result = FieldFormatter.normalize_date("nan", DateFormat.YYYY_MM_DD)
        assert result is None

    def test_normalize_float_none_input(self):
        """测试浮点数None输入"""
        result = FieldFormatter.normalize_float(None)
        assert result is None

        result = FieldFormatter.normalize_float("")
        assert result is None

    def test_normalize_int_none_input(self):
        """测试整数None输入"""
        result = FieldFormatter.normalize_int(None)
        assert result is None


class TestFieldTypeDetection:
    """测试字段类型检测"""

    def test_detect_amount_type(self):
        """测试金额类型检测"""
        validator = FieldValidator()

        assert validator._infer_field_type("buy_amount") == FieldType.AMOUNT
        assert validator._infer_field_type("sell_amount") == FieldType.AMOUNT
        assert validator._infer_field_type("total_amount") == FieldType.AMOUNT

    def test_detect_rate_type(self):
        """测试比率类型检测"""
        validator = FieldValidator()

        assert validator._infer_field_type("growth_rate") == FieldType.RATE
        assert validator._infer_field_type("turnover_rate") == FieldType.RATE

    def test_detect_boolean_type(self):
        """测试布尔类型检测"""
        validator = FieldValidator()

        assert validator._infer_field_type("is_st") == FieldType.BOOLEAN
        assert validator._infer_field_type("has_dividend") == FieldType.BOOLEAN

    def test_detect_net_flow_type(self):
        """测试净流量类型检测"""
        validator = FieldValidator()

        assert validator._infer_field_type("main_net_inflow") == FieldType.NET_FLOW
        assert validator._infer_field_type("super_large_net_outflow") == FieldType.NET_FLOW


class TestChineseToEnglishMapping:
    """测试中英文映射"""

    def test_chinese_market_suffix(self):
        """测试中文市场后缀"""
        result = FieldFormatter.normalize_stock_code("000001上证", StockCodeFormat.WITH_SUFFIX)
        assert ".SH" in result

        result = FieldFormatter.normalize_stock_code("000001深证", StockCodeFormat.WITH_SUFFIX)
        assert ".SZ" in result

    def test_chinese_boolean_values(self):
        """测试中文布尔值"""
        assert FieldFormatter.normalize_boolean("是") is True
        assert FieldFormatter.normalize_boolean("对") is True
        assert FieldFormatter.normalize_boolean("真") is True
        assert FieldFormatter.normalize_boolean("否") is False
        assert FieldFormatter.normalize_boolean("错") is False
        assert FieldFormatter.normalize_boolean("假") is False

    def test_chinese_date_format(self):
        """测试中文日期格式"""
        result = FieldFormatter.normalize_date("2024年12月31日", DateFormat.YYYY_MM_DD)
        assert result == "2024-12-31"


class TestFieldPrefixRules:
    """测试字段前缀规则"""

    def test_boolean_prefix_is(self):
        """测试布尔前缀is_"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("is_st", FieldType.BOOLEAN)
        assert is_valid is True

        is_valid, _, _ = validator.validate_field_name("st", FieldType.BOOLEAN)
        assert is_valid is False

    def test_boolean_prefix_has(self):
        """测试布尔前缀has_"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("has_dividend", FieldType.BOOLEAN)
        assert is_valid is True

    def test_boolean_suggestion_adds_prefix(self):
        """测试布尔字段建议添加前缀"""
        validator = FieldValidator()

        suggestion = validator._suggest_field_name("st", FieldType.BOOLEAN)
        assert suggestion.startswith("is_")

    def test_stock_code_prefix_sh(self):
        """测试SH前缀"""
        result = FieldFormatter.normalize_stock_code("sh600000", StockCodeFormat.PURE_NUMERIC)
        assert result == "600000"

    def test_stock_code_prefix_sz(self):
        """测试SZ前缀"""
        result = FieldFormatter.normalize_stock_code("sz000001", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"


class TestFieldSuffixRules:
    """测试字段后缀规则"""

    def test_amount_suffix(self):
        """测试金额后缀"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("buy_amount", FieldType.AMOUNT)
        assert is_valid is True

        is_valid, _, _ = validator.validate_field_name("buy", FieldType.AMOUNT)
        assert is_valid is False

    def test_rate_suffix(self):
        """测试比率后缀"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("growth_rate", FieldType.RATE)
        assert is_valid is True

    def test_ratio_suffix(self):
        """测试比例后缀"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("holdings_ratio", FieldType.RATIO)
        assert is_valid is True

    def test_date_suffix_for_event(self):
        """测试事件日期后缀"""
        validator = FieldValidator()

        is_valid, _, _ = validator.validate_field_name("report_date", FieldType.EVENT_DATE)
        assert is_valid is True

        is_valid, _, _ = validator.validate_field_name("date", FieldType.EVENT_DATE)
        assert is_valid is False

    def test_suggestion_adds_suffix(self):
        """测试建议添加后缀"""
        validator = FieldValidator()

        suggestion = validator._suggest_field_name("buy", FieldType.AMOUNT)
        assert suggestion.endswith("_amount")


class TestInvalidFieldNameHandling:
    """测试无效字段名处理"""

    def test_invalid_stock_code_returns_original(self):
        """测试无效股票代码返回原值"""
        result = FieldFormatter.normalize_stock_code("ABC", StockCodeFormat.PURE_NUMERIC)
        assert result == "ABC"

    def test_invalid_date_returns_original(self):
        """测试无效日期返回原值"""
        result = FieldFormatter.normalize_date("invalid_date", DateFormat.YYYY_MM_DD)
        assert result == "invalid_date"

    def test_invalid_float_returns_none(self):
        """测试无效浮点数返回None"""
        result = FieldFormatter.normalize_float("not_a_number")
        assert result is None

    def test_field_validator_handles_unknown_type(self):
        """测试验证器处理未知类型"""
        validator = FieldValidator()

        df = pd.DataFrame({"unknown_field": [1, 2]})
        results = validator.validate_dataframe(df)

        assert "unknown_field" in results
        assert results["unknown_field"].field_type == FieldType.OTHER
        assert results["unknown_field"].is_valid is True

    def test_field_mapper_missing_required_columns(self):
        """测试映射器缺少必要列"""
        mapper = FieldMapper()

        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="missing_col", standard_field="date", field_type=FieldType.DATE),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        df = pd.DataFrame({"other_col": [1, 2]})
        result = mapper.map_fields(df, "test_source", "test_module")

        assert "other_col" in result.columns
        assert "date" not in result.columns


class TestValidateFieldName:
    """Test the validate_field_name method."""

    def test_validate_valid_date_field(self):
        """Test validation of valid date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("date", FieldType.DATE)

        assert is_valid is True
        assert error_msg is None

    def test_validate_invalid_date_field(self):
        """Test validation of invalid date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("trading_date", FieldType.DATE)

        assert is_valid is False
        assert error_msg is not None
        assert "date" in error_msg.lower()

    def test_validate_valid_event_date_field(self):
        """Test validation of valid event date fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["report_date", "announcement_date", "pledge_date"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
            assert is_valid is True
            assert error_msg is None

    def test_validate_invalid_event_date_field(self):
        """Test validation of invalid event date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("date", FieldType.EVENT_DATE)

        assert is_valid is False
        assert error_msg is not None

    def test_validate_valid_amount_field(self):
        """Test validation of valid amount fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["buy_amount", "sell_amount", "total_amount"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.AMOUNT)
            assert is_valid is True
            assert error_msg is None

    def test_validate_invalid_amount_field(self):
        """Test validation of invalid amount field."""
        standardizer = FieldStandardizer(NamingRules())
        # Test invalid CamelCase field name
        is_valid, error_msg = standardizer.validate_field_name("BuyAmount", FieldType.AMOUNT)

        assert is_valid is False
        assert "pattern" in error_msg.lower()

    def test_validate_valid_net_flow_field(self):
        """Test validation of valid net flow fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["main_net_inflow", "super_large_net_outflow", "northbound_net_buy"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.NET_FLOW)
            assert is_valid is True
            assert error_msg is None

    def test_validate_invalid_net_flow_field(self):
        """Test validation of invalid net flow field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("net_inflow", FieldType.NET_FLOW)

        assert is_valid is False
        assert error_msg is not None

    def test_validate_valid_rate_field(self):
        """Test validation of valid rate fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["growth_rate", "turnover_rate", "pct_change"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.RATE)
            assert is_valid is True
            assert error_msg is None

    def test_validate_valid_ratio_field(self):
        """Test validation of valid ratio fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["holdings_ratio", "pledge_ratio"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.RATIO)
            assert is_valid is True
            assert error_msg is None

    def test_validate_valid_symbol_field(self):
        """Test validation of valid symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("symbol", FieldType.SYMBOL)

        assert is_valid is True
        assert error_msg is None

    def test_validate_invalid_symbol_field(self):
        """Test validation of invalid symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("stock_symbol", FieldType.SYMBOL)

        assert is_valid is False
        assert "symbol" in error_msg.lower()

    def test_validate_valid_boolean_field(self):
        """Test validation of valid boolean fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["is_st", "has_dividend", "is_suspended"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.BOOLEAN)
            assert is_valid is True
            assert error_msg is None

    def test_validate_invalid_boolean_field(self):
        """Test validation of invalid boolean field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("suspended", FieldType.BOOLEAN)

        assert is_valid is False
        assert error_msg is not None

    def test_validate_other_field_type(self):
        """Test validation of OTHER field type (accepts any pattern)."""
        standardizer = FieldStandardizer(NamingRules())

        # OTHER type should accept any field name
        for field_name in ["any_field", "AnyField", "123"]:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.OTHER)
            assert is_valid is True
            assert error_msg is None

    def test_error_message_contains_suggestion(self):
        """Test that error messages contain helpful suggestions."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name("trading_date", FieldType.DATE)

        assert is_valid is False
        assert "Expected pattern" in error_msg
        assert "Suggestion" in error_msg


class TestStandardizeFieldName:
    """Test the standardize_field_name method."""

    def test_standardize_valid_field_name(self):
        """Test standardizing a valid field name."""
        standardizer = FieldStandardizer(NamingRules())
        result = standardizer.standardize_field_name("date", FieldType.DATE)

        assert result == "date"

    def test_standardize_valid_event_date_field(self):
        """Test standardizing valid event date fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["report_date", "announcement_date", "pledge_date"]:
            result = standardizer.standardize_field_name(field_name, FieldType.EVENT_DATE)
            assert result == field_name

    def test_standardize_valid_amount_field(self):
        """Test standardizing valid amount fields."""
        standardizer = FieldStandardizer(NamingRules())

        for field_name in ["buy_amount", "sell_amount", "total_amount"]:
            result = standardizer.standardize_field_name(field_name, FieldType.AMOUNT)
            assert result == field_name

    def test_standardize_invalid_field_name_raises_error(self):
        """Test that standardizing an invalid field name raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())

        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name("trading_date", FieldType.DATE)

        assert "does not conform to naming rules" in str(exc_info.value)
        assert "trading_date" in str(exc_info.value)

    def test_standardize_invalid_amount_field_raises_error(self):
        """Test that standardizing an invalid amount field raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())

        # Test invalid CamelCase field name (should raise error)
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name("BuyAmount", FieldType.AMOUNT)

        assert "does not conform to naming rules" in str(exc_info.value)
        assert "BuyAmount" in str(exc_info.value)

    def test_standardize_invalid_symbol_field_raises_error(self):
        """Test that standardizing an invalid symbol field raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())

        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name("stock_symbol", FieldType.SYMBOL)

        assert "does not conform to naming rules" in str(exc_info.value)
        assert "symbol" in str(exc_info.value).lower()

    def test_error_message_includes_field_type(self):
        """Test that error message includes the field type."""
        standardizer = FieldStandardizer(NamingRules())

        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name("invalid_date", FieldType.DATE)

        assert "date" in str(exc_info.value).lower()


class TestStandardizeDataFrame:
    """Test the standardize_dataframe method."""

    def test_standardize_dataframe_with_valid_fields(self):
        """Test standardizing a DataFrame with all valid field names."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "symbol": ["000001", "000002"],
                "buy_amount": [1000000, 2000000],
                "sell_amount": [800000, 1500000],
            }
        )

        field_mapping = {
            "date": FieldType.DATE,
            "symbol": FieldType.SYMBOL,
            "buy_amount": FieldType.AMOUNT,
            "sell_amount": FieldType.AMOUNT,
        }

        result = standardizer.standardize_dataframe(df, field_mapping)

        # Should return a DataFrame with the same columns
        assert list(result.columns) == list(df.columns)
        # Should not modify the original DataFrame
        assert result is not df
        # Data should be preserved
        pd.testing.assert_frame_equal(result, df)

    def test_standardize_dataframe_with_invalid_field_raises_error(self):
        """Test that standardizing a DataFrame with invalid field name raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame({"trading_date": ["2024-01-01", "2024-01-02"], "symbol": ["000001", "000002"]})

        field_mapping = {"trading_date": FieldType.DATE, "symbol": FieldType.SYMBOL}

        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_dataframe(df, field_mapping)

        assert "trading_date" in str(exc_info.value)
        assert "does not conform to naming rules" in str(exc_info.value)

    def test_standardize_dataframe_with_partial_mapping(self):
        """Test standardizing a DataFrame where only some fields are in the mapping."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "symbol": ["000001", "000002"], "unmapped_field": [100, 200]}
        )

        # Only map some fields
        field_mapping = {"date": FieldType.DATE, "symbol": FieldType.SYMBOL}

        result = standardizer.standardize_dataframe(df, field_mapping)

        # Should succeed and return DataFrame with all columns
        assert list(result.columns) == list(df.columns)
        pd.testing.assert_frame_equal(result, df)

    def test_standardize_empty_dataframe(self):
        """Test standardizing an empty DataFrame."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame()
        field_mapping = {}

        result = standardizer.standardize_dataframe(df, field_mapping)

        assert result.empty
        assert result is not df

    def test_standardize_dataframe_with_complex_field_types(self):
        """Test standardizing a DataFrame with various field types."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "report_date": ["2024-01-15"],
                "symbol": ["000001"],
                "name": ["Test Stock"],
                "buy_amount": [1000000],
                "main_net_inflow": [500000],
                "turnover_rate": [0.05],
                "holdings_ratio": [0.15],
                "is_st": [False],
                "volume": [10000000],
            }
        )

        field_mapping = {
            "date": FieldType.DATE,
            "report_date": FieldType.EVENT_DATE,
            "symbol": FieldType.SYMBOL,
            "name": FieldType.NAME,
            "buy_amount": FieldType.AMOUNT,
            "main_net_inflow": FieldType.NET_FLOW,
            "turnover_rate": FieldType.RATE,
            "holdings_ratio": FieldType.RATIO,
            "is_st": FieldType.BOOLEAN,
            "volume": FieldType.VOLUME,
        }

        result = standardizer.standardize_dataframe(df, field_mapping)

        # All fields should be valid
        assert list(result.columns) == list(df.columns)
        pd.testing.assert_frame_equal(result, df)

    def test_standardize_dataframe_does_not_modify_original(self):
        """Test that standardize_dataframe does not modify the original DataFrame."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "symbol": ["000001", "000002"]})

        original_df = df.copy()

        field_mapping = {"date": FieldType.DATE, "symbol": FieldType.SYMBOL}

        result = standardizer.standardize_dataframe(df, field_mapping)

        # Original DataFrame should be unchanged
        pd.testing.assert_frame_equal(df, original_df)
        # Result should be a different object
        assert result is not df

    def test_standardize_dataframe_with_multiple_invalid_fields(self):
        """Test that the first invalid field causes an error."""
        standardizer = FieldStandardizer(NamingRules())

        df = pd.DataFrame({"trading_date": ["2024-01-01"], "stock_symbol": ["000001"], "amount": [1000000]})

        field_mapping = {"trading_date": FieldType.DATE, "stock_symbol": FieldType.SYMBOL, "amount": FieldType.AMOUNT}

        # Should raise error for one of the invalid fields
        with pytest.raises(ValueError):
            standardizer.standardize_dataframe(df, field_mapping)


class TestGenerateErrorMessage:
    """Test the _generate_error_message helper method."""

    def test_error_message_for_date_field(self):
        """Test error message generation for date field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r"^date$"
        error_msg = standardizer._generate_error_message("trading_date", FieldType.DATE, pattern)

        assert "Expected pattern" in error_msg
        assert "Suggestion" in error_msg
        assert "date" in error_msg.lower()

    def test_error_message_for_amount_field(self):
        """Test error message generation for amount field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r"^[a-z_]+_amount$"
        error_msg = standardizer._generate_error_message("amount", FieldType.AMOUNT, pattern)

        assert "Expected pattern" in error_msg
        assert "Suggestion" in error_msg
        assert "buy_amount" in error_msg or "sell_amount" in error_msg

    def test_error_message_for_symbol_field(self):
        """Test error message generation for symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = "^symbol$"
        error_msg = standardizer._generate_error_message("stock_symbol", FieldType.SYMBOL, pattern)

        assert "Expected pattern" in error_msg
        assert "Suggestion" in error_msg
        assert "symbol" in error_msg.lower()

    def test_error_message_for_boolean_field(self):
        """Test error message generation for boolean field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r"^(is|has)_[a-z_]+$"
        error_msg = standardizer._generate_error_message("suspended", FieldType.BOOLEAN, pattern)

        assert "Expected pattern" in error_msg
        assert "Suggestion" in error_msg
        assert "is_" in error_msg or "has_" in error_msg


class TestFieldFormatterComprehensive:
    """Comprehensive tests for FieldFormatter - formatter.py"""

    def test_format_date_yyyymmdd(self):
        """Test YYYYMMDD date format conversion"""
        assert FieldFormatter.normalize_date("2024-01-01", DateFormat.YYYYMMDD) == "20240101"
        assert FieldFormatter.normalize_date("2024-12-31", DateFormat.YYYYMMDD) == "20241231"
        assert FieldFormatter.normalize_date("20240101", DateFormat.YYYYMMDD) == "20240101"

    def test_format_date_yyyy_mm_dd(self):
        """Test YYYY-MM-DD date format"""
        assert FieldFormatter.normalize_date("20240101", DateFormat.YYYY_MM_DD) == "2024-01-01"
        assert FieldFormatter.normalize_date("20241231", DateFormat.YYYY_MM_DD) == "2024-12-31"
        assert FieldFormatter.normalize_date("2024/01/01", DateFormat.YYYY_MM_DD) == "2024-01-01"

    def test_format_date_chinese(self):
        """Test Chinese date format conversion"""
        assert FieldFormatter.normalize_date("2024年1月1日", DateFormat.YYYY_MM_DD) == "2024-01-01"
        assert FieldFormatter.normalize_date("2024年12月31日", DateFormat.YYYY_MM_DD) == "2024-12-31"
        assert FieldFormatter.normalize_date("2024年01月01日", DateFormat.YYYYMMDD) == "20240101"

    def test_format_date_iso(self):
        """Test ISO date format"""
        assert (
            FieldFormatter.normalize_date("2024-01-01T00:00:00", DateFormat.YYYY_MM_DD_HH_MM_SS)
            == "2024-01-01 00:00:00"
        )
        assert (
            FieldFormatter.normalize_date("2024-01-01 12:30:45", DateFormat.YYYY_MM_DD_HH_MM_SS)
            == "2024-01-01 12:30:45"
        )

    def test_format_date_invalid(self):
        """Test invalid date handling"""
        assert FieldFormatter.normalize_date("not-a-date", DateFormat.YYYY_MM_DD) == "not-a-date"
        assert FieldFormatter.normalize_date("", DateFormat.YYYY_MM_DD) is None
        assert FieldFormatter.normalize_date("none", DateFormat.YYYY_MM_DD) is None
        assert FieldFormatter.normalize_date("null", DateFormat.YYYY_MM_DD) is None

    def test_format_date_yyyymm(self):
        """Test YYYYMM format"""
        assert FieldFormatter.normalize_date("2024-01", DateFormat.YYYYMM) == "202401"
        assert FieldFormatter.normalize_date("202401", DateFormat.YYYYMM) == "202401"
        assert FieldFormatter.normalize_date("2024-12", DateFormat.YYYYMM) == "202412"

    def test_format_date_yyyy_mm(self):
        """Test YYYY-MM format"""
        assert FieldFormatter.normalize_date("202401", DateFormat.YYYY_MM) == "2024-01"
        assert FieldFormatter.normalize_date("2024-01", DateFormat.YYYY_MM) == "2024-01"

    def test_format_number_with_commas(self):
        """Test number formatting with commas"""
        assert FieldFormatter.normalize_float("1,234,567.89") == 1234567.89
        assert FieldFormatter.normalize_float("9,999,999") == 9999999.0
        assert FieldFormatter.normalize_float("1,234") == 1234.0

    def test_format_number_decimal_places(self):
        """Test number with various decimal places"""
        assert FieldFormatter.normalize_float("123.456") == 123.456
        assert FieldFormatter.normalize_float("0.123456") == 0.123456
        assert FieldFormatter.normalize_float("1000.00") == 1000.0

    def test_format_percentage(self):
        """Test percentage formatting"""
        assert FieldFormatter.normalize_float("20.5%") == 0.205
        assert FieldFormatter.normalize_float("100%") == 1.0
        assert FieldFormatter.normalize_float("0.5%") == 0.005
        assert FieldFormatter.normalize_float("50%%") == 0.5

    def test_format_currency(self):
        """Test currency formatting"""
        assert FieldFormatter.normalize_float("$1,234.56") == 1234.56
        assert FieldFormatter.normalize_float("¥100") == 100.0
        assert FieldFormatter.normalize_float("¥1,000") == 1000.0

    def test_format_large_number(self):
        """Test large number formatting"""
        assert FieldFormatter.normalize_float("1000000000") == 1000000000.0
        assert FieldFormatter.normalize_float("1234567890123") == 1234567890123.0

    def test_format_symbol_sh(self):
        """Test SH stock code formatting"""
        result = FieldFormatter.normalize_stock_code("sh600000", StockCodeFormat.WITH_SUFFIX)
        assert result == "600000.SH"
        result = FieldFormatter.normalize_stock_code("SH600000", StockCodeFormat.WITH_SUFFIX)
        assert result == "600000.SH"

    def test_format_symbol_sz(self):
        """Test SZ stock code formatting"""
        result = FieldFormatter.normalize_stock_code("sz000001", StockCodeFormat.WITH_SUFFIX)
        assert result == "000001.SZ"
        result = FieldFormatter.normalize_stock_code("SZ000001", StockCodeFormat.WITH_SUFFIX)
        assert result == "000001.SZ"

    def test_format_symbol_bj(self):
        """Test BJ stock code formatting"""
        result = FieldFormatter.normalize_stock_code("bj430001", StockCodeFormat.WITH_SUFFIX)
        assert result == "430001.BJ"
        result = FieldFormatter.normalize_stock_code("BJ430001", StockCodeFormat.WITH_SUFFIX)
        assert result == "430001.BJ"

    def test_format_symbol_with_exchange(self):
        """Test stock code with explicit exchange"""
        result = FieldFormatter.normalize_stock_code("600000.SH", StockCodeFormat.WITH_PREFIX)
        assert result == "sh600000"
        result = FieldFormatter.normalize_stock_code("000001.SZ", StockCodeFormat.WITH_PREFIX)
        assert result == "sz000001"

    def test_format_symbol_invalid(self):
        """Test invalid stock code"""
        result = FieldFormatter.normalize_stock_code("invalid", StockCodeFormat.PURE_NUMERIC)
        assert result == "invalid"

    def test_add_market_suffix_sh(self):
        """Test adding SH market suffix"""
        result = FieldFormatter.normalize_stock_code("600000", StockCodeFormat.WITH_SUFFIX, default_market="sh")
        assert ".SH" in result

    def test_add_market_suffix_sz(self):
        """Test adding SZ market suffix"""
        result = FieldFormatter.normalize_stock_code("000001", StockCodeFormat.WITH_SUFFIX, default_market="sz")
        assert ".SZ" in result

    def test_add_market_suffix_auto(self):
        """Test auto market suffix detection"""
        result = FieldFormatter.normalize_stock_code("600000", StockCodeFormat.WITH_SUFFIX, default_market="auto")
        assert ".SH" in result
        result = FieldFormatter.normalize_stock_code("000001", StockCodeFormat.WITH_SUFFIX, default_market="auto")
        assert ".SZ" in result

    def test_chinese_market_suffixes(self):
        """Test Chinese market suffix mapping"""
        result = FieldFormatter.normalize_stock_code("600000上证", StockCodeFormat.WITH_SUFFIX)
        assert ".SH" in result
        result = FieldFormatter.normalize_stock_code("000001深证", StockCodeFormat.WITH_SUFFIX)
        assert ".SZ" in result
        result = FieldFormatter.normalize_stock_code("430001北证", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result

    def test_chinese_market_prefixes(self):
        """Test Chinese market prefix mapping"""
        result = FieldFormatter.normalize_stock_code("上证600000", StockCodeFormat.WITH_SUFFIX)
        assert ".SH" in result
        result = FieldFormatter.normalize_stock_code("深证000001", StockCodeFormat.WITH_SUFFIX)
        assert ".SZ" in result

    def test_numeric_only_code(self):
        """Test numeric-only stock code"""
        result = FieldFormatter.normalize_stock_code("600000", StockCodeFormat.PURE_NUMERIC)
        assert result == "600000"
        result = FieldFormatter.normalize_stock_code(600000, StockCodeFormat.PURE_NUMERIC)
        assert result == "600000"

    def test_code_padding(self):
        """Test stock code zero-padding"""
        result = FieldFormatter.normalize_stock_code("1", StockCodeFormat.PURE_NUMERIC)
        assert result == "000001"
        result = FieldFormatter.normalize_stock_code("12", StockCodeFormat.PURE_NUMERIC)
        assert result == "000012"
        result = FieldFormatter.normalize_stock_code("12345", StockCodeFormat.PURE_NUMERIC)
        assert result == "012345"

    def test_float_negative_values(self):
        """Test negative float values"""
        assert FieldFormatter.normalize_float("-100.5") == -100.5
        assert FieldFormatter.normalize_float("-0.5%") == -0.005
        assert FieldFormatter.normalize_float("-1,234.56") == -1234.56

    def test_float_plus_sign(self):
        """Test float with plus sign"""
        assert FieldFormatter.normalize_float("+100.5") == 100.5
        assert FieldFormatter.normalize_float("+0.5%") == 0.005

    def test_float_invalid_returns_none(self):
        """Test invalid float returns None"""
        assert FieldFormatter.normalize_float("abc") is None
        assert FieldFormatter.normalize_float("") is None
        assert FieldFormatter.normalize_float("-") is None

    def test_int_from_float(self):
        """Test integer from float conversion"""
        assert FieldFormatter.normalize_int(123.6) == 124
        assert FieldFormatter.normalize_int(123.4) == 123
        assert FieldFormatter.normalize_int(123.5) == 124

    def test_int_from_string(self):
        """Test integer from string conversion"""
        assert FieldFormatter.normalize_int("123") == 123
        assert FieldFormatter.normalize_int("123.6") == 124
        assert FieldFormatter.normalize_int("abc") is None

    def test_boolean_various_values(self):
        """Test various boolean values"""
        assert FieldFormatter.normalize_boolean(True) is True
        assert FieldFormatter.normalize_boolean(False) is False
        assert FieldFormatter.normalize_boolean("1") is True
        assert FieldFormatter.normalize_boolean("0") is False
        assert FieldFormatter.normalize_boolean("T") is True
        assert FieldFormatter.normalize_boolean("F") is False

    def test_boolean_chinese_values(self):
        """Test Chinese boolean values"""
        assert FieldFormatter.normalize_boolean("是") is True
        assert FieldFormatter.normalize_boolean("否") is False
        assert FieldFormatter.normalize_boolean("对") is True
        assert FieldFormatter.normalize_boolean("错") is False
        assert FieldFormatter.normalize_boolean("真") is True
        assert FieldFormatter.normalize_boolean("假") is False

    def test_boolean_invalid_returns_none(self):
        """Test invalid boolean returns None"""
        assert FieldFormatter.normalize_boolean("maybe") is None
        assert FieldFormatter.normalize_boolean("unknown") is None
        assert FieldFormatter.normalize_boolean(None) is None


class TestShortcutFunctions:
    """Test shortcut functions in formatter module"""

    def test_format_stock_code_pure(self):
        """Test format_stock_code with pure format"""
        assert format_stock_code("sh600000", "pure") == "600000"
        assert format_stock_code("600000.SH", "pure") == "600000"

    def test_format_stock_code_suffix(self):
        """Test format_stock_code with suffix format"""
        assert format_stock_code("sh600000", "suffix") == "600000.SH"
        assert format_stock_code("600000", "suffix") == "600000.SH"

    def test_format_stock_code_prefix(self):
        """Test format_stock_code with prefix format"""
        assert format_stock_code("sh600000", "prefix") == "sh600000"
        assert format_stock_code("600000.SH", "prefix") == "sh600000"

    def test_format_stock_code_numeric(self):
        """Test format_stock_code with numeric format"""
        assert format_stock_code("sh600000", "numeric") == "600000"

    def test_format_stock_code_with_suffix(self):
        """Test format_stock_code with with_suffix format"""
        assert format_stock_code("sh600000", "with_suffix") == "600000.SH"

    def test_format_stock_code_with_prefix(self):
        """Test format_stock_code with with_prefix format"""
        assert format_stock_code("600000.SH", "with_prefix") == "sh600000"

    def test_format_date_ymd(self):
        """Test format_date with ymd format"""
        assert format_date("20240101", "ymd") == "2024-01-01"
        assert format_date("2024-01-01", "ymd") == "2024-01-01"

    def test_format_date_yyyymmdd(self):
        """Test format_date with yyyymmdd format"""
        assert format_date("2024-01-01", "yyyymmdd") == "20240101"

    def test_format_date_ym(self):
        """Test format_date with ym format"""
        assert format_date("2024-01", "ym") == "202401"
        assert format_date("202401", "ym") == "202401"

    def test_format_date_yyyy_mm(self):
        """Test format_date with yyyy-mm format"""
        assert format_date("202401", "yyyy-mm") == "2024-01"

    def test_format_date_ymd_hms(self):
        """Test format_date with ymd_hms format"""
        assert format_date("2024-01-01 12:30:45", "ymd_hms") == "2024-01-01 12:30:45"
        assert format_date("2024-01-01", "ymd_hms") == "2024-01-01 00:00:00"

    def test_format_float_value(self):
        """Test format_float shortcut"""
        assert format_float("123.45") == 123.45
        assert format_float("1,234.56") == 1234.56
        assert format_float("50%") == 0.5

    def test_format_int_value(self):
        """Test format_int shortcut"""
        assert format_int("123") == 123
        assert format_int(123.6) == 124

    def test_format_boolean_value(self):
        """Test format_boolean shortcut"""
        assert format_boolean("yes") is True
        assert format_boolean("no") is False


class TestFieldMapperComprehensive:
    """Comprehensive tests for FieldMapper - field_mapper.py"""

    def test_load_mappings_from_directory(self):
        """Test loading mappings from directory"""
        mapper = FieldMapper()
        assert isinstance(mapper.mappings, dict)

    def test_map_fields_empty_dataframe(self):
        """Test mapping with empty DataFrame"""
        mapper = FieldMapper()
        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="日期", standard_field="date", field_type=FieldType.DATE),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        df = pd.DataFrame()
        result = mapper.map_fields(df, "test_source", "test_module")
        assert len(result.columns) == 0

    def test_map_fields_partial_match(self):
        """Test mapping with partial column match"""
        mapper = FieldMapper()
        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="日期", standard_field="date", field_type=FieldType.DATE),
                FieldMapping(source_field="不存在的列", standard_field="nonexistent", field_type=FieldType.DATE),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        df = pd.DataFrame({"日期": ["2024-01-01"], "其他列": [100]})
        result = mapper.map_fields(df, "test_source", "test_module")

        assert "date" in result.columns
        assert "其他列" in result.columns
        assert "nonexistent" not in result.columns

    def test_add_mapping_updates_existing(self):
        """Test add_mapping updates existing mapping"""
        mapper = FieldMapper()

        mapping1 = FieldMapping(source_field="日期", standard_field="date", field_type=FieldType.DATE)
        mapper.add_mapping("test_source", "test_module", mapping1)

        mapping2 = FieldMapping(source_field="日期", standard_field="new_date", field_type=FieldType.DATE)
        mapper.add_mapping("test_source", "test_module", mapping2)

        config = mapper.mappings["test_source"]["test_module"]
        date_mapping = next((m for m in config.mappings if m.source_field == "日期"), None)
        assert date_mapping is not None
        assert date_mapping.standard_field == "new_date"

    def test_get_mapping_nonexistent(self):
        """Test get_mapping with nonexistent field"""
        mapper = FieldMapper()
        mapping = mapper.get_mapping("test_source", "test_module", "nonexistent")
        assert mapping is None

    def test_get_mapping_nonexistent_source_module(self):
        """Test get_mapping with nonexistent source/module"""
        mapper = FieldMapper()
        mapping = mapper.get_mapping("nonexistent_source", "nonexistent_module", "field")
        assert mapping is None

    def test_map_fields_no_matching_columns(self):
        """Test mapping when no columns match"""
        mapper = FieldMapper()
        config = MappingConfig(
            source="test_source",
            module="test_module",
            mappings=[
                FieldMapping(source_field="不存在", standard_field="missing", field_type=FieldType.DATE),
            ],
        )
        mapper.mappings["test_source"] = {"test_module": config}

        df = pd.DataFrame({"日期": ["2024-01-01"]})
        result = mapper.map_fields(df, "test_source", "test_module")

        assert "日期" in result.columns
        assert "missing" not in result.columns


class TestAliasManagerComprehensive:
    """Comprehensive tests for FieldAliasManager - alias_manager.py"""

    def test_add_aliases_to_dataframe_with_duplicates(self):
        """Test adding aliases when alias columns already exist"""
        alias_config = {"old_price": "price"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"price": [10.0], "old_price": [20.0]})
        result = manager.add_aliases_to_dataframe(df)

        assert result["old_price"].equals(result["price"])

    def test_add_aliases_to_dataframe_empty(self):
        """Test adding aliases to empty DataFrame"""
        alias_config = {"old_field": "new_field"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"new_field": []})
        result = manager.add_aliases_to_dataframe(df)

        assert "old_field" in result.columns

    def test_resolve_field_access_with_warning(self):
        """Test field access with deprecation warning enabled"""
        alias_config = {"deprecated": "current"}
        manager = FieldAliasManager(alias_config, enable_warnings=True)

        df = pd.DataFrame({"current": [1, 2, 3]})

        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = manager.resolve_field_access(df, "deprecated")
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message)
            assert "current" in str(w[0].message)

    def test_resolve_field_access_standard_field(self):
        """Test resolving standard field access"""
        alias_config = {"old": "new"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"new": [1, 2, 3], "old": [4, 5, 6]})

        result = manager.resolve_field_access(df, "new")
        assert result.equals(df["new"])

    def test_resolve_field_access_missing_standard_field(self):
        """Test resolving when standard field is missing"""
        alias_config = {"deprecated": "current"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"other": [1, 2, 3]})

        with pytest.raises(KeyError) as exc_info:
            manager.resolve_field_access(df, "deprecated")

        assert "current" in str(exc_info.value)

    def test_add_alias_updates_reverse_mapping(self):
        """Test add_alias updates reverse_aliases"""
        alias_config = {"old1": "new1"}
        manager = FieldAliasManager(alias_config)

        manager.add_alias("old2", "new1")

        assert "old2" in manager.reverse_aliases["new1"]
        assert len(manager.reverse_aliases["new1"]) == 2

    def test_remove_alias_updates_reverse_mapping(self):
        """Test remove_alias updates reverse_aliases"""
        alias_config = {"old1": "new1", "old2": "new1"}
        manager = FieldAliasManager(alias_config)

        manager.remove_alias("old1")

        assert "old1" not in manager.reverse_aliases["new1"]
        assert "old2" in manager.reverse_aliases["new1"]

    def test_remove_alias_last_reverse_mapping(self):
        """Test remove_alias removes reverse mapping when last"""
        alias_config = {"old1": "new1"}
        manager = FieldAliasManager(alias_config)

        manager.remove_alias("old1")

        assert "new1" not in manager.reverse_aliases

    def test_get_all_aliases_returns_copy(self):
        """Test get_all_aliases returns a copy"""
        alias_config = {"old": "new"}
        manager = FieldAliasManager(alias_config)

        aliases = manager.get_all_aliases()
        aliases["old"] = "modified"

        assert manager.aliases["old"] == "new"

    def test_alias_manager_multiple_aliases_same_field(self):
        """Test multiple aliases pointing to same field"""
        alias_config = {"alias1": "standard", "alias2": "standard"}
        manager = FieldAliasManager(alias_config)

        df = pd.DataFrame({"standard": [1, 2, 3]})
        result = manager.add_aliases_to_dataframe(df)

        assert "alias1" in result.columns
        assert "alias2" in result.columns


class TestFieldValidatorComprehensive:
    """Comprehensive tests for FieldValidator - field_validator.py"""

    def test_validate_dataframe_with_whitelist(self):
        """Test DataFrame validation with whitelist"""
        validator = FieldValidator(whitelist={"whitelisted_field"})

        df = pd.DataFrame({"whitelisted_field": ["test"], "invalid_field": ["test"]})
        results = validator.validate_dataframe(df)

        assert results["whitelisted_field"].is_valid is True
        assert results["whitelisted_field"].field_type is None

    def test_validate_field_name_whitelist(self):
        """Test field name validation with whitelist"""
        validator = FieldValidator(whitelist={"special_field"})

        is_valid, error_msg, suggested = validator.validate_field_name("special_field", FieldType.DATE)
        assert is_valid is True
        assert error_msg is None
        assert suggested is None

    def test_validate_field_name_unknown_type(self):
        """Test validation with unknown field type"""
        validator = FieldValidator()

        is_valid, error_msg, suggested = validator.validate_field_name("test_field", FieldType.OTHER)

        assert is_valid is True

    def test_remove_from_whitelist(self):
        """Test removing from whitelist"""
        validator = FieldValidator(whitelist={"test_field"})

        validator.remove_from_whitelist("test_field")
        assert "test_field" not in validator.whitelist

    def test_remove_from_whitelist_not_exists(self):
        """Test removing from whitelist when not exists"""
        validator = FieldValidator()

        validator.remove_from_whitelist("nonexistent")
        assert "nonexistent" not in validator.whitelist

    def test_load_whitelist_from_file(self, tmp_path):
        """Test loading whitelist from file"""
        whitelist_file = tmp_path / "whitelist.json"
        whitelist_file.write_text('{"whitelist": ["field1", "field2", "field3"]}')

        validator = FieldValidator()
        validator.load_whitelist(str(whitelist_file))

        assert "field1" in validator.whitelist
        assert "field2" in validator.whitelist
        assert "field3" in validator.whitelist

    def test_load_whitelist_from_list_file(self, tmp_path):
        """Test loading whitelist from list format file"""
        whitelist_file = tmp_path / "whitelist.json"
        whitelist_file.write_text('["field_a", "field_b"]')

        validator = FieldValidator()
        validator.load_whitelist(str(whitelist_file))

        assert "field_a" in validator.whitelist
        assert "field_b" in validator.whitelist

    def test_load_whitelist_file_not_found(self, tmp_path):
        """Test loading whitelist when file not found"""
        validator = FieldValidator()
        validator.load_whitelist(str(tmp_path / "nonexistent.json"))

        assert len(validator.whitelist) == 0

    def test_save_whitelist(self, tmp_path):
        """Test saving whitelist to file"""
        validator = FieldValidator(whitelist={"field1", "field2"})
        whitelist_file = tmp_path / "whitelist.json"

        validator.save_whitelist(str(whitelist_file))

        import json

        with open(whitelist_file) as f:
            data = json.load(f)

        assert "whitelist" in data
        assert len(data["whitelist"]) == 2
        assert data["count"] == 2

    def test_validation_summary_statistics(self):
        """Test validation summary generates correct statistics"""
        validator = FieldValidator()

        results = {
            "date": ValidationResult(field_name="date", is_valid=True, field_type=FieldType.DATE),
            "symbol": ValidationResult(field_name="symbol", is_valid=True, field_type=FieldType.SYMBOL),
            "invalid_field": ValidationResult(
                field_name="invalid_field", is_valid=False, field_type=FieldType.AMOUNT, error_message="error"
            ),
        }

        summary = validator.get_validation_summary(results)

        assert summary["total_fields"] == 3
        assert summary["valid_fields"] == 2
        assert summary["invalid_fields"] == 1
        assert summary["validation_rate"] == 2 / 3

    def test_validation_summary_type_statistics(self):
        """Test validation summary type statistics"""
        validator = FieldValidator()

        results = {
            "date": ValidationResult(field_name="date", is_valid=True, field_type=FieldType.DATE),
            "symbol": ValidationResult(field_name="symbol", is_valid=True, field_type=FieldType.SYMBOL),
            "amount": ValidationResult(field_name="amount", is_valid=True, field_type=FieldType.AMOUNT),
        }

        summary = validator.get_validation_summary(results)

        assert "date" in summary["type_statistics"]
        assert summary["type_statistics"]["date"]["total"] == 1
        assert summary["type_statistics"]["date"]["valid"] == 1

    def test_validation_summary_invalid_field_details(self):
        """Test validation summary includes invalid field details"""
        validator = FieldValidator()

        results = {
            "invalid_field": ValidationResult(
                field_name="invalid_field",
                is_valid=False,
                field_type=FieldType.AMOUNT,
                error_message="does not conform",
                suggested_name="suggested_field",
            ),
        }

        summary = validator.get_validation_summary(results)

        assert len(summary["invalid_field_details"]) == 1
        detail = summary["invalid_field_details"][0]
        assert detail["field_name"] == "invalid_field"
        assert detail["suggested_name"] == "suggested_field"

    def test_validation_summary_empty_results(self):
        """Test validation summary with empty results"""
        validator = FieldValidator()

        summary = validator.get_validation_summary({})

        assert summary["total_fields"] == 0
        assert summary["valid_fields"] == 0
        assert summary["validation_rate"] == 0

    def test_validate_dataframe_infers_types(self):
        """Test validate_dataframe infers field types"""
        validator = FieldValidator()

        df = pd.DataFrame({"date": ["2024-01-01"], "buy_amount": [100]})
        results = validator.validate_dataframe(df)

        assert results["date"].field_type == FieldType.DATE
        assert results["buy_amount"].field_type == FieldType.AMOUNT

    def test_validate_dataframe_with_provided_types(self):
        """Test validate_dataframe uses provided types over inference"""
        validator = FieldValidator()

        df = pd.DataFrame({"date": ["2024-01-01"]})
        field_types = {"date": FieldType.TIMESTAMP}
        results = validator.validate_dataframe(df, field_types)

        assert results["date"].field_type == FieldType.TIMESTAMP

    def test_suggest_field_name_with_existing_suffix(self):
        """Test suggest_field_name doesn't add duplicate suffix"""
        validator = FieldValidator()

        suggestion = validator._suggest_field_name("buy_amount", FieldType.AMOUNT)
        assert suggestion == "buy_amount"

    def test_suggest_field_name_boolean(self):
        """Test suggest_field_name for boolean fields"""
        validator = FieldValidator()

        suggestion = validator._suggest_field_name("st", FieldType.BOOLEAN)
        assert suggestion.startswith("is_")

    def test_suggest_field_name_net_flow(self):
        """Test suggest_field_name for net flow fields"""
        validator = FieldValidator()

        suggestion = validator._suggest_field_name("main_inflow", FieldType.NET_FLOW)
        assert "_net_" in suggestion or "main" in suggestion

    def test_infer_field_type_exact_matches(self):
        """Test field type inference with exact matches"""
        validator = FieldValidator()

        assert validator._infer_field_type("date") == FieldType.DATE
        assert validator._infer_field_type("timestamp") == FieldType.TIMESTAMP
        assert validator._infer_field_type("symbol") == FieldType.SYMBOL
        assert validator._infer_field_type("name") == FieldType.NAME
        assert validator._infer_field_type("market") == FieldType.MARKET
        assert validator._infer_field_type("rank") == FieldType.RANK
        assert validator._infer_field_type("volume") == FieldType.VOLUME

    def test_infer_field_type_pattern_matches(self):
        """Test field type inference with pattern matches"""
        validator = FieldValidator()

        assert validator._infer_field_type("buy_amount") == FieldType.AMOUNT
        assert validator._infer_field_type("report_date") == FieldType.EVENT_DATE
        assert validator._infer_field_type("turnover_rate") == FieldType.RATE
        assert validator._infer_field_type("holdings_ratio") == FieldType.RATIO
        assert validator._infer_field_type("main_net_inflow") == FieldType.NET_FLOW
        assert validator._infer_field_type("is_st") == FieldType.BOOLEAN

    def test_generate_error_message_all_types(self):
        """Test error message generation for all field types"""
        validator = FieldValidator()

        for field_type in FieldType:
            if field_type != FieldType.OTHER:
                error_msg = validator._generate_error_message("test_field", field_type, r"^pattern$")
                assert "test_field" in error_msg

    def test_validate_field_name_with_pattern(self):
        """Test validate_field_name with pattern"""
        validator = FieldValidator()

        is_valid, error_msg, suggested = validator.validate_field_name("test_field", FieldType.CODE)

        assert isinstance(is_valid, bool)

    def test_whitelist_operations(self):
        """Test whitelist add and remove operations"""
        validator = FieldValidator()

        validator.add_to_whitelist("field1")
        validator.add_to_whitelist("field2")
        assert "field1" in validator.whitelist
        assert "field2" in validator.whitelist

        validator.remove_from_whitelist("field1")
        assert "field1" not in validator.whitelist
        assert "field2" in validator.whitelist


class TestFieldMappingConfig:
    """Test MappingConfig and FieldMapping models"""

    def test_field_mapping_apply_with_transform(self):
        """Test FieldMapping apply with custom transform"""
        mapping = FieldMapping(
            source_field="price", standard_field="amount", field_type=FieldType.AMOUNT, transform=lambda x: x * 100
        )

        assert mapping.apply(10) == 1000

    def test_field_mapping_apply_without_transform(self):
        """Test FieldMapping apply without transform"""
        mapping = FieldMapping(source_field="price", standard_field="amount", field_type=FieldType.AMOUNT)

        assert mapping.apply(10) == 10

    def test_mapping_config_to_dict(self):
        """Test MappingConfig to_dict"""
        config = MappingConfig(
            source="test",
            module="test_module",
            mappings=[FieldMapping(source_field="a", standard_field="b", field_type=FieldType.DATE)],
        )

        result = config.to_dict()

        assert result["source"] == "test"
        assert result["module"] == "test_module"
        assert len(result["mappings"]) == 1

    def test_mapping_config_from_dict(self):
        """Test MappingConfig from_dict"""
        data = {
            "source": "test",
            "module": "test_module",
            "mappings": [
                {"source_field": "日期", "standard_field": "date", "field_type": "date", "target_unit": "yuan"}
            ],
        }

        config = MappingConfig.from_dict(data)

        assert config.source == "test"
        assert config.module == "test_module"
        assert len(config.mappings) == 1
        assert config.mappings[0].source_field == "日期"

    def test_mapping_config_from_dict_with_missing_fields(self):
        """Test MappingConfig from_dict with missing fields"""
        data = {"source": "test", "module": "test_module", "mappings": [{"source_field": "a"}]}

        config = MappingConfig.from_dict(data)

        assert len(config.mappings) == 0

    def test_mapping_config_from_dict_with_invalid_type(self):
        """Test MappingConfig from_dict with invalid field type"""
        data = {
            "source": "test",
            "module": "test_module",
            "mappings": [{"source_field": "a", "standard_field": "b", "field_type": "invalid_type"}],
        }

        config = MappingConfig.from_dict(data)

        assert len(config.mappings) == 1
        assert config.mappings[0].field_type == FieldType.OTHER


class TestDateFormatEdgeCases:
    """Test edge cases for date formatting"""

    def test_date_with_extra_zeros(self):
        """Test date with extra leading zeros"""
        assert FieldFormatter.normalize_date("2024-01-01", DateFormat.YYYYMMDD) == "20240101"
        assert FieldFormatter.normalize_date("0001-01-01", DateFormat.YYYYMMDD) == "00010101"

    def test_date_february_29(self):
        """Test February 29 on leap year"""
        result = FieldFormatter.normalize_date("2024-02-29", DateFormat.YYYYMMDD)
        assert result == "20240229"

    def test_date_time_with_milliseconds(self):
        """Test datetime with milliseconds"""
        result = FieldFormatter.normalize_date("2024-01-01 12:30:45.123", DateFormat.YYYY_MM_DD_HH_MM_SS)
        assert result == "2024-01-01 12:30:45"

    def test_date_only_year(self):
        """Test date with only year"""
        result = FieldFormatter.normalize_date("2024", DateFormat.YYYY_MM_DD)
        assert result == "2024-01-01"

    def test_date_edge_months(self):
        """Test dates at month boundaries"""
        assert FieldFormatter.normalize_date("2024-01-31", DateFormat.YYYYMMDD) == "20240131"
        assert FieldFormatter.normalize_date("2024-12-01", DateFormat.YYYYMMDD) == "20241201"


class TestFloatEdgeCases:
    """Test edge cases for float formatting"""

    def test_float_scientific_notation(self):
        """Test float with scientific notation"""
        result = FieldFormatter.normalize_float("1e5")
        assert result is None or isinstance(result, float)

    def test_float_leading_zeros(self):
        """Test float with leading zeros"""
        assert FieldFormatter.normalize_float("0.123") == 0.123
        assert FieldFormatter.normalize_float("00.123") == 0.123

    def test_float_only_decimals(self):
        """Test float with only decimal point"""
        assert FieldFormatter.normalize_float(".5") == 0.5
        assert FieldFormatter.normalize_float(".") is None


class TestStockCodeEdgeCases:
    """Test edge cases for stock code formatting"""

    def test_stock_code_8_digit(self):
        """Test 8-digit stock code"""
        result = FieldFormatter.normalize_stock_code("12345678", StockCodeFormat.PURE_NUMERIC)
        assert result == "12345678"

    def test_stock_code_with_spaces(self):
        """Test stock code with spaces"""
        result = FieldFormatter.normalize_stock_code("  600000  ", StockCodeFormat.PURE_NUMERIC)
        assert result == "600000"

    def test_stock_code_bj_auto_detection(self):
        """Test BJ stock code auto detection"""
        result = FieldFormatter.normalize_stock_code("430001", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result

    def test_stock_code_special_bj_codes(self):
        """Test special BJ codes starting with 8, 4, 9"""
        result = FieldFormatter.normalize_stock_code("830001", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result
        result = FieldFormatter.normalize_stock_code("430001", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result
        result = FieldFormatter.normalize_stock_code("920001", StockCodeFormat.WITH_SUFFIX)
        assert ".BJ" in result


class TestNamingRulesModel:
    """Test NamingRules model"""

    def test_naming_rules_validate_valid_names(self):
        """Test NamingRules validation with valid names"""
        rules = NamingRules()

        assert rules.validate_field_name("date", FieldType.DATE) is True
        assert rules.validate_field_name("report_date", FieldType.EVENT_DATE) is True
        assert rules.validate_field_name("buy_amount", FieldType.AMOUNT) is True

    def test_naming_rules_validate_invalid_names(self):
        """Test NamingRules validation with invalid names"""
        rules = NamingRules()

        assert rules.validate_field_name("Date", FieldType.DATE) is False
        assert rules.validate_field_name("invalid_date", FieldType.DATE) is False

    def test_naming_rules_get_pattern_for_type(self):
        """Test NamingRules _get_pattern_for_type"""
        rules = NamingRules()

        pattern = rules._get_pattern_for_type(FieldType.DATE)
        assert pattern == rules.date_field_pattern

        pattern = rules._get_pattern_for_type(FieldType.OTHER)
        assert pattern == r".*"
