"""
Unit tests for field naming standardization data models.

Tests the core data models including FieldType enum, NamingRules,
FieldMapping, and MappingConfig classes.
"""

from akshare_one.modules.field_naming import (
    FieldMapping,
    FieldType,
    MappingConfig,
    NamingRules,
)


class TestFieldType:
    """Test the FieldType enum."""
    
    def test_field_type_enum_values(self):
        """Test that all FieldType enum values are correctly defined."""
        # 日期/时间类型
        assert FieldType.DATE.value == 'date'
        assert FieldType.TIMESTAMP.value == 'timestamp'
        assert FieldType.EVENT_DATE.value == 'event_date'
        assert FieldType.TIME.value == 'time'
        assert FieldType.DURATION.value == 'duration'
        
        # 金额类型
        assert FieldType.AMOUNT.value == 'amount'
        assert FieldType.BALANCE.value == 'balance'
        assert FieldType.VALUE.value == 'value'
        assert FieldType.NET_FLOW.value == 'net_flow'
        
        # 比率类型
        assert FieldType.RATE.value == 'rate'
        assert FieldType.RATIO.value == 'ratio'
        
        # 标识符类型
        assert FieldType.SYMBOL.value == 'symbol'
        assert FieldType.NAME.value == 'name'
        assert FieldType.CODE.value == 'code'
        assert FieldType.MARKET.value == 'market'
        assert FieldType.RANK.value == 'rank'
        
        # 数量类型
        assert FieldType.COUNT.value == 'count'
        assert FieldType.VOLUME.value == 'volume'
        assert FieldType.SHARES.value == 'shares'
        
        # 特殊类型
        assert FieldType.BOOLEAN.value == 'boolean'
        assert FieldType.TYPE.value == 'type'
        assert FieldType.OTHER.value == 'other'
    
    def test_field_type_enum_count(self):
        """Test that all expected field types are present."""
        # 应该有 22 个字段类型
        assert len(FieldType) == 22


class TestNamingRules:
    """Test the NamingRules dataclass."""
    
    def test_naming_rules_default_initialization(self):
        """Test that NamingRules can be initialized with defaults."""
        rules = NamingRules()
        assert rules.date_field_pattern == r'^date$'
        assert rules.timestamp_field_name == 'timestamp'
        assert rules.symbol_field_name == 'symbol'
        assert rules.name_field_name == 'name'
    
    def test_validate_date_field_name(self):
        """Test validation of date field names."""
        rules = NamingRules()
        
        # Valid date field
        assert rules.validate_field_name('date', FieldType.DATE) is True
        
        # Invalid date field
        assert rules.validate_field_name('trading_date', FieldType.DATE) is False
        assert rules.validate_field_name('Date', FieldType.DATE) is False
    
    def test_validate_event_date_field_name(self):
        """Test validation of event date field names."""
        rules = NamingRules()
        
        # Valid event date fields
        assert rules.validate_field_name('report_date', FieldType.EVENT_DATE) is True
        assert rules.validate_field_name('announcement_date', FieldType.EVENT_DATE) is True
        assert rules.validate_field_name('pledge_date', FieldType.EVENT_DATE) is True
        
        # Invalid event date fields
        assert rules.validate_field_name('date', FieldType.EVENT_DATE) is False
        assert rules.validate_field_name('ReportDate', FieldType.EVENT_DATE) is False
    
    def test_validate_timestamp_field_name(self):
        """Test validation of timestamp field names."""
        rules = NamingRules()
        
        # Valid timestamp field
        assert rules.validate_field_name('timestamp', FieldType.TIMESTAMP) is True
        
        # Invalid timestamp field
        assert rules.validate_field_name('time_stamp', FieldType.TIMESTAMP) is False
        assert rules.validate_field_name('ts', FieldType.TIMESTAMP) is False
    
    def test_validate_time_field_name(self):
        """Test validation of time field names."""
        rules = NamingRules()
        
        # Valid time fields
        assert rules.validate_field_name('limit_up_time', FieldType.TIME) is True
        assert rules.validate_field_name('limit_down_time', FieldType.TIME) is True
        
        # Invalid time fields
        assert rules.validate_field_name('time', FieldType.TIME) is False
        assert rules.validate_field_name('LimitUpTime', FieldType.TIME) is False
    
    def test_validate_duration_field_name(self):
        """Test validation of duration field names."""
        rules = NamingRules()
        
        # Valid duration fields
        assert rules.validate_field_name('consecutive_days', FieldType.DURATION) is True
        assert rules.validate_field_name('holding_duration', FieldType.DURATION) is True
        
        # Invalid duration fields
        assert rules.validate_field_name('days', FieldType.DURATION) is False
        assert rules.validate_field_name('duration', FieldType.DURATION) is False
    
    def test_validate_amount_field_name(self):
        """Test validation of amount field names."""
        rules = NamingRules()
        
        # Valid amount fields
        assert rules.validate_field_name('buy_amount', FieldType.AMOUNT) is True
        assert rules.validate_field_name('sell_amount', FieldType.AMOUNT) is True
        assert rules.validate_field_name('total_amount', FieldType.AMOUNT) is True
        
        # Invalid amount fields
        assert rules.validate_field_name('amount', FieldType.AMOUNT) is False
        assert rules.validate_field_name('BuyAmount', FieldType.AMOUNT) is False
    
    def test_validate_balance_field_name(self):
        """Test validation of balance field names."""
        rules = NamingRules()
        
        # Valid balance fields
        assert rules.validate_field_name('margin_balance', FieldType.BALANCE) is True
        assert rules.validate_field_name('total_balance', FieldType.BALANCE) is True
        
        # Invalid balance fields
        assert rules.validate_field_name('balance', FieldType.BALANCE) is False
    
    def test_validate_value_field_name(self):
        """Test validation of value field names."""
        rules = NamingRules()
        
        # Valid value fields
        assert rules.validate_field_name('market_value', FieldType.VALUE) is True
        assert rules.validate_field_name('holdings_value', FieldType.VALUE) is True
        
        # Invalid value fields
        assert rules.validate_field_name('value', FieldType.VALUE) is False
    
    def test_validate_net_flow_field_name(self):
        """Test validation of net flow field names."""
        rules = NamingRules()
        
        # Valid net flow fields
        assert rules.validate_field_name('main_net_inflow', FieldType.NET_FLOW) is True
        assert rules.validate_field_name('super_large_net_outflow', FieldType.NET_FLOW) is True
        assert rules.validate_field_name('northbound_net_buy', FieldType.NET_FLOW) is True
        assert rules.validate_field_name('foreign_net_sell', FieldType.NET_FLOW) is True
        
        # Invalid net flow fields
        assert rules.validate_field_name('net_inflow', FieldType.NET_FLOW) is False
        assert rules.validate_field_name('main_inflow', FieldType.NET_FLOW) is False
    
    def test_validate_rate_field_name(self):
        """Test validation of rate field names."""
        rules = NamingRules()
        
        # Valid rate fields
        assert rules.validate_field_name('growth_rate', FieldType.RATE) is True
        assert rules.validate_field_name('turnover_rate', FieldType.RATE) is True
        assert rules.validate_field_name('pct_change', FieldType.RATE) is True
        assert rules.validate_field_name('broken_rate', FieldType.RATE) is True
        
        # Invalid rate fields
        assert rules.validate_field_name('rate', FieldType.RATE) is False
    
    def test_validate_ratio_field_name(self):
        """Test validation of ratio field names."""
        rules = NamingRules()
        
        # Valid ratio fields
        assert rules.validate_field_name('holdings_ratio', FieldType.RATIO) is True
        assert rules.validate_field_name('pledge_ratio', FieldType.RATIO) is True
        
        # Invalid ratio fields
        assert rules.validate_field_name('ratio', FieldType.RATIO) is False
    
    def test_validate_symbol_field_name(self):
        """Test validation of symbol field names."""
        rules = NamingRules()
        
        # Valid symbol field
        assert rules.validate_field_name('symbol', FieldType.SYMBOL) is True
        
        # Invalid symbol fields
        assert rules.validate_field_name('stock_symbol', FieldType.SYMBOL) is False
        assert rules.validate_field_name('code', FieldType.SYMBOL) is False
    
    def test_validate_name_field_name(self):
        """Test validation of name field names."""
        rules = NamingRules()
        
        # Valid name field
        assert rules.validate_field_name('name', FieldType.NAME) is True
        
        # Invalid name fields
        assert rules.validate_field_name('stock_name', FieldType.NAME) is False
    
    def test_validate_code_field_name(self):
        """Test validation of code field names."""
        rules = NamingRules()
        
        # Valid code fields
        assert rules.validate_field_name('sector_code', FieldType.CODE) is True
        assert rules.validate_field_name('industry_code', FieldType.CODE) is True
        
        # Invalid code fields
        assert rules.validate_field_name('code', FieldType.CODE) is False
    
    def test_validate_market_field_name(self):
        """Test validation of market field names."""
        rules = NamingRules()
        
        # Valid market field
        assert rules.validate_field_name('market', FieldType.MARKET) is True
        
        # Invalid market fields
        assert rules.validate_field_name('market_type', FieldType.MARKET) is False
    
    def test_validate_rank_field_name(self):
        """Test validation of rank field names."""
        rules = NamingRules()
        
        # Valid rank field
        assert rules.validate_field_name('rank', FieldType.RANK) is True
        
        # Invalid rank fields
        assert rules.validate_field_name('ranking', FieldType.RANK) is False
    
    def test_validate_count_field_name(self):
        """Test validation of count field names."""
        rules = NamingRules()
        
        # Valid count fields
        assert rules.validate_field_name('constituent_count', FieldType.COUNT) is True
        assert rules.validate_field_name('open_count', FieldType.COUNT) is True
        
        # Invalid count fields
        assert rules.validate_field_name('count', FieldType.COUNT) is False
    
    def test_validate_volume_field_name(self):
        """Test validation of volume field names."""
        rules = NamingRules()
        
        # Valid volume field
        assert rules.validate_field_name('volume', FieldType.VOLUME) is True
        
        # Invalid volume fields
        assert rules.validate_field_name('trade_volume', FieldType.VOLUME) is False
    
    def test_validate_shares_field_name(self):
        """Test validation of shares field names."""
        rules = NamingRules()
        
        # Valid shares fields
        assert rules.validate_field_name('holdings_shares', FieldType.SHARES) is True
        assert rules.validate_field_name('pledge_shares', FieldType.SHARES) is True
        
        # Invalid shares fields
        assert rules.validate_field_name('shares', FieldType.SHARES) is False
    
    def test_validate_boolean_field_name(self):
        """Test validation of boolean field names."""
        rules = NamingRules()
        
        # Valid boolean fields
        assert rules.validate_field_name('is_st', FieldType.BOOLEAN) is True
        assert rules.validate_field_name('has_dividend', FieldType.BOOLEAN) is True
        assert rules.validate_field_name('is_suspended', FieldType.BOOLEAN) is True
        
        # Invalid boolean fields
        assert rules.validate_field_name('st', FieldType.BOOLEAN) is False
        assert rules.validate_field_name('suspended', FieldType.BOOLEAN) is False
    
    def test_validate_type_field_name(self):
        """Test validation of type field names."""
        rules = NamingRules()
        
        # Valid type fields
        assert rules.validate_field_name('sector_type', FieldType.TYPE) is True
        assert rules.validate_field_name('release_category', FieldType.TYPE) is True
        
        # Invalid type fields
        assert rules.validate_field_name('type', FieldType.TYPE) is False
    
    def test_validate_other_field_type(self):
        """Test validation of OTHER field type (accepts any pattern)."""
        rules = NamingRules()
        
        # OTHER type should accept any field name
        assert rules.validate_field_name('any_field_name', FieldType.OTHER) is True
        assert rules.validate_field_name('AnyFieldName', FieldType.OTHER) is True
        assert rules.validate_field_name('123', FieldType.OTHER) is True


class TestFieldMapping:
    """Test the FieldMapping dataclass."""
    
    def test_field_mapping_initialization(self):
        """Test that FieldMapping can be initialized correctly."""
        mapping = FieldMapping(
            source_field='日期',
            standard_field='date',
            field_type=FieldType.DATE,
            description='交易日期'
        )
        
        assert mapping.source_field == '日期'
        assert mapping.standard_field == 'date'
        assert mapping.field_type == FieldType.DATE
        assert mapping.source_unit is None
        assert mapping.target_unit == 'yuan'
        assert mapping.transform is None
        assert mapping.description == '交易日期'
    
    def test_field_mapping_with_unit_conversion(self):
        """Test FieldMapping with unit conversion information."""
        mapping = FieldMapping(
            source_field='主力净流入',
            standard_field='main_net_inflow',
            field_type=FieldType.NET_FLOW,
            source_unit='yi_yuan',
            target_unit='yuan',
            description='主力资金净流入'
        )
        
        assert mapping.source_unit == 'yi_yuan'
        assert mapping.target_unit == 'yuan'
    
    def test_field_mapping_apply_without_transform(self):
        """Test apply method without custom transform function."""
        mapping = FieldMapping(
            source_field='日期',
            standard_field='date',
            field_type=FieldType.DATE
        )
        
        # Without transform, should return value as-is
        assert mapping.apply('2024-01-01') == '2024-01-01'
        assert mapping.apply(123) == 123
    
    def test_field_mapping_apply_with_transform(self):
        """Test apply method with custom transform function."""
        # Custom transform: multiply by 100000000 (亿元 to 元)
        mapping = FieldMapping(
            source_field='主力净流入',
            standard_field='main_net_inflow',
            field_type=FieldType.NET_FLOW,
            source_unit='yi_yuan',
            target_unit='yuan',
            transform=lambda x: x * 100000000
        )
        
        assert mapping.apply(1.5) == 150000000
        assert mapping.apply(0.1) == 10000000


class TestMappingConfig:
    """Test the MappingConfig dataclass."""
    
    def test_mapping_config_initialization(self):
        """Test that MappingConfig can be initialized correctly."""
        config = MappingConfig(
            source='eastmoney',
            module='fundflow',
            version='1.0',
            last_updated='2024-01-01'
        )
        
        assert config.source == 'eastmoney'
        assert config.module == 'fundflow'
        assert config.version == '1.0'
        assert config.last_updated == '2024-01-01'
        assert config.mappings == []
    
    def test_mapping_config_with_mappings(self):
        """Test MappingConfig with field mappings."""
        mapping1 = FieldMapping(
            source_field='日期',
            standard_field='date',
            field_type=FieldType.DATE
        )
        mapping2 = FieldMapping(
            source_field='主力净流入',
            standard_field='main_net_inflow',
            field_type=FieldType.NET_FLOW
        )
        
        config = MappingConfig(
            source='eastmoney',
            module='fundflow',
            mappings=[mapping1, mapping2]
        )
        
        assert len(config.mappings) == 2
        assert config.mappings[0].source_field == '日期'
        assert config.mappings[1].source_field == '主力净流入'
    
    def test_mapping_config_to_dict(self):
        """Test serialization of MappingConfig to dictionary."""
        mapping = FieldMapping(
            source_field='日期',
            standard_field='date',
            field_type=FieldType.DATE,
            description='交易日期'
        )
        
        config = MappingConfig(
            source='eastmoney',
            module='fundflow',
            mappings=[mapping],
            version='1.0',
            last_updated='2024-01-01'
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['source'] == 'eastmoney'
        assert config_dict['module'] == 'fundflow'
        assert config_dict['version'] == '1.0'
        assert config_dict['last_updated'] == '2024-01-01'
        assert len(config_dict['mappings']) == 1
        assert config_dict['mappings'][0]['source_field'] == '日期'
        assert config_dict['mappings'][0]['standard_field'] == 'date'
        assert config_dict['mappings'][0]['field_type'] == 'date'
        assert config_dict['mappings'][0]['description'] == '交易日期'
    
    def test_mapping_config_from_dict(self):
        """Test deserialization of MappingConfig from dictionary."""
        config_dict = {
            'source': 'eastmoney',
            'module': 'fundflow',
            'version': '1.0',
            'last_updated': '2024-01-01',
            'mappings': [
                {
                    'source_field': '日期',
                    'standard_field': 'date',
                    'field_type': 'date',
                    'source_unit': None,
                    'target_unit': 'yuan',
                    'description': '交易日期'
                },
                {
                    'source_field': '主力净流入',
                    'standard_field': 'main_net_inflow',
                    'field_type': 'net_flow',
                    'source_unit': 'yi_yuan',
                    'target_unit': 'yuan',
                    'description': '主力资金净流入'
                }
            ]
        }
        
        config = MappingConfig.from_dict(config_dict)
        
        assert config.source == 'eastmoney'
        assert config.module == 'fundflow'
        assert config.version == '1.0'
        assert config.last_updated == '2024-01-01'
        assert len(config.mappings) == 2
        assert config.mappings[0].source_field == '日期'
        assert config.mappings[0].standard_field == 'date'
        assert config.mappings[0].field_type == FieldType.DATE
        assert config.mappings[1].source_unit == 'yi_yuan'
    
    def test_mapping_config_roundtrip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        mapping = FieldMapping(
            source_field='主力净流入',
            standard_field='main_net_inflow',
            field_type=FieldType.NET_FLOW,
            source_unit='yi_yuan',
            target_unit='yuan',
            description='主力资金净流入'
        )
        
        original_config = MappingConfig(
            source='eastmoney',
            module='fundflow',
            mappings=[mapping],
            version='1.0',
            last_updated='2024-01-01'
        )
        
        # Serialize and deserialize
        config_dict = original_config.to_dict()
        restored_config = MappingConfig.from_dict(config_dict)
        
        # Verify all fields match
        assert restored_config.source == original_config.source
        assert restored_config.module == original_config.module
        assert restored_config.version == original_config.version
        assert restored_config.last_updated == original_config.last_updated
        assert len(restored_config.mappings) == len(original_config.mappings)
        assert restored_config.mappings[0].source_field == original_config.mappings[0].source_field
        assert restored_config.mappings[0].standard_field == original_config.mappings[0].standard_field
        assert restored_config.mappings[0].field_type == original_config.mappings[0].field_type
        assert restored_config.mappings[0].source_unit == original_config.mappings[0].source_unit
    
    def test_mapping_config_from_dict_with_missing_optional_fields(self):
        """Test deserialization with missing optional fields."""
        config_dict = {
            'source': 'eastmoney',
            'module': 'fundflow',
            'mappings': [
                {
                    'source_field': '日期',
                    'standard_field': 'date',
                    'field_type': 'date'
                }
            ]
        }
        
        config = MappingConfig.from_dict(config_dict)
        
        assert config.version == '1.0'  # Default value
        assert config.last_updated == ''  # Default value
        assert config.mappings[0].source_unit is None
        assert config.mappings[0].target_unit == 'yuan'  # Default value
        assert config.mappings[0].description == ''  # Default value
    
    def test_mapping_config_from_dict_with_empty_mappings(self):
        """Test deserialization with empty mappings list."""
        config_dict = {
            'source': 'eastmoney',
            'module': 'fundflow'
        }
        
        config = MappingConfig.from_dict(config_dict)
        
        assert config.mappings == []
