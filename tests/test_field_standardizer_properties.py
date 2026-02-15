"""
Property-based tests for FieldStandardizer.

Tests the date and time field naming properties using Hypothesis for property-based testing.

Feature: field-naming-standardization
Task: 2.3 为 FieldStandardizer 编写属性测试
"""

import re
from datetime import datetime, timedelta
import pandas as pd
import pytest

try:
    from hypothesis import given, strategies as st, assume, settings
    from hypothesis.extra.pandas import column, data_frames
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("Hypothesis not installed", allow_module_level=True)

from akshare_one.modules.field_naming import (
    FieldStandardizer,
    NamingRules,
    FieldType,
)


# ============================================================================
# Test Data Generators (Hypothesis Strategies)
# ============================================================================

@st.composite
def valid_date_field_names(draw):
    """Generate valid date field names according to naming rules."""
    # For DATE type, only 'date' is valid
    return 'date'


@st.composite
def valid_event_date_field_names(draw):
    """Generate valid event date field names (pattern: {event}_date)."""
    event_prefixes = ['report', 'announcement', 'pledge', 'release', 
                      'disclosure', 'dividend', 'listing', 'delisting',
                      'suspension', 'resumption', 'audit', 'approval']
    event = draw(st.sampled_from(event_prefixes))
    return f'{event}_date'


@st.composite
def valid_time_field_names(draw):
    """Generate valid time field names (pattern: {event}_time)."""
    event_prefixes = ['limit_up', 'limit_down', 'open', 'close', 
                      'trading', 'auction', 'break', 'resume']
    event = draw(st.sampled_from(event_prefixes))
    return f'{event}_time'


@st.composite
def valid_duration_field_names(draw):
    """Generate valid duration field names (pattern: {metric}_days or {metric}_duration)."""
    metric_prefixes = ['consecutive', 'holding', 'trading', 'suspension',
                       'lock', 'waiting', 'settlement']
    metric = draw(st.sampled_from(metric_prefixes))
    suffix = draw(st.sampled_from(['days', 'duration']))
    return f'{metric}_{suffix}'


@st.composite
def date_strings(draw):
    """Generate date strings in YYYY-MM-DD format."""
    year = draw(st.integers(min_value=2000, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Safe for all months
    return f'{year:04d}-{month:02d}-{day:02d}'


@st.composite
def time_strings(draw):
    """Generate time strings in HH:MM:SS format."""
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    second = draw(st.integers(min_value=0, max_value=59))
    return f'{hour:02d}:{minute:02d}:{second:02d}'


@st.composite
def timestamp_strings(draw):
    """Generate timestamp strings in YYYY-MM-DD HH:MM:SS format."""
    date_str = draw(date_strings())
    time_str = draw(time_strings())
    return f'{date_str} {time_str}'


# ============================================================================
# Property 1: 日期字段命名和格式一致性
# **Validates: Requirements 1.1, 1.2**
# ============================================================================

class TestProperty1DateFieldNamingConsistency:
    """
    Property 1: 日期字段命名和格式一致性
    
    对于任何包含日期数据的 DataFrame，如果字段表示日级或更长周期的主时间字段，
    则该字段应命名为 `date` 且格式为 YYYY-MM-DD；如果表示日内数据，
    则应命名为 `timestamp` 且包含时区信息
    
    **Validates: Requirements 1.1, 1.2**
    """
    
    @given(field_name=valid_date_field_names())
    @settings(max_examples=100)
    def test_date_field_must_be_named_date(self, field_name):
        """
        Property: For any date field representing daily or longer period data,
        the field must be named 'date'.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # The field name should be 'date'
        assert field_name == 'date'
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.DATE)
        assert is_valid is True
        assert error_msg is None
    
    @given(
        invalid_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_',
            min_size=1,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_non_date_field_names_rejected_for_date_type(self, invalid_name):
        """
        Property: Any field name other than 'date' should be rejected for DATE type.
        """
        assume(invalid_name != 'date')  # Skip if it happens to be 'date'
        
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name(invalid_name, FieldType.DATE)
        
        # Should be invalid
        assert is_valid is False
        assert error_msg is not None
    
    def test_timestamp_field_must_be_named_timestamp(self):
        """
        Property: For any field representing intraday data with time,
        the field must be named 'timestamp'.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # 'timestamp' should be valid
        is_valid, error_msg = standardizer.validate_field_name('timestamp', FieldType.TIMESTAMP)
        assert is_valid is True
        assert error_msg is None
        
        # Other names should be invalid
        for invalid_name in ['time_stamp', 'ts', 'datetime', 'time']:
            is_valid, error_msg = standardizer.validate_field_name(invalid_name, FieldType.TIMESTAMP)
            assert is_valid is False
    
    @given(date_str=date_strings())
    @settings(max_examples=50)
    def test_date_format_validation(self, date_str):
        """
        Property: Date strings should follow YYYY-MM-DD format.
        """
        # Verify the generated date string matches the expected format
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'

        assert re.match(date_pattern, date_str) is not None
        
        # Verify it can be parsed as a valid date
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pytest.fail(f"Generated date string '{date_str}' is not a valid date")


# ============================================================================
# Property 2: 事件日期字段命名模式
# **Validates: Requirements 1.3**
# ============================================================================

class TestProperty2EventDateFieldNamingPattern:
    """
    Property 2: 事件日期字段命名模式
    
    对于任何表示特定事件日期的字段，字段名应匹配模式 `{event}_date`
    （如 `report_date`、`announcement_date`、`pledge_date`）
    
    **Validates: Requirements 1.3**
    """
    
    @given(field_name=valid_event_date_field_names())
    @settings(max_examples=100)
    def test_event_date_fields_match_pattern(self, field_name):
        """
        Property: All event date field names must match the pattern {event}_date.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # Field name should match the pattern
        event_date_pattern = r'^[a-z_]+_date$'

        assert re.match(event_date_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
        assert is_valid is True
        assert error_msg is None
    
    @given(
        event=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz_',
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_event_date_pattern_structure(self, event):
        """
        Property: Event date fields must have the structure {event}_date.
        """
        assume(len(event) > 0 and event[0] != '_' and event[-1] != '_')
        assume('__' not in event)  # No double underscores
        
        field_name = f'{event}_date'
        standardizer = FieldStandardizer(NamingRules())
        
        # Should match the pattern
        event_date_pattern = r'^[a-z_]+_date$'

        assert re.match(event_date_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
        assert is_valid is True
    
    def test_plain_date_rejected_for_event_date_type(self):
        """
        Property: The plain 'date' field should not be valid for EVENT_DATE type.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # 'date' should be invalid for EVENT_DATE
        is_valid, error_msg = standardizer.validate_field_name('date', FieldType.EVENT_DATE)
        assert is_valid is False
        assert error_msg is not None
    
    @given(
        invalid_suffix=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz',
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_event_fields_without_date_suffix_rejected(self, invalid_suffix):
        """
        Property: Event fields without '_date' suffix should be rejected.
        """
        assume(invalid_suffix != 'date')
        
        field_name = f'report_{invalid_suffix}'
        standardizer = FieldStandardizer(NamingRules())
        
        is_valid, _ = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
        assert is_valid is False


# ============================================================================
# Property 3: 时间点字段命名和格式
# **Validates: Requirements 1.4, 12.3**
# ============================================================================

class TestProperty3TimeFieldNamingAndFormat:
    """
    Property 3: 时间点字段命名和格式
    
    对于任何表示一天内具体时间点的字段，字段名应匹配模式 `{event}_time` 
    且格式为 HH:MM:SS
    
    **Validates: Requirements 1.4, 12.3**
    """
    
    @given(field_name=valid_time_field_names())
    @settings(max_examples=100)
    def test_time_fields_match_pattern(self, field_name):
        """
        Property: All time field names must match the pattern {event}_time.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # Field name should match the pattern
        time_pattern = r'^[a-z_]+_time$'

        assert re.match(time_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.TIME)
        assert is_valid is True
        assert error_msg is None
    
    @given(
        event=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz_',
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_time_field_pattern_structure(self, event):
        """
        Property: Time fields must have the structure {event}_time.
        """
        assume(len(event) > 0 and event[0] != '_' and event[-1] != '_')
        assume('__' not in event)  # No double underscores
        
        field_name = f'{event}_time'
        standardizer = FieldStandardizer(NamingRules())
        
        # Should match the pattern
        time_pattern = r'^[a-z_]+_time$'

        assert re.match(time_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.TIME)
        assert is_valid is True
    
    def test_plain_time_rejected_for_time_type(self):
        """
        Property: The plain 'time' field should not be valid for TIME type.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # 'time' should be invalid for TIME type
        is_valid, error_msg = standardizer.validate_field_name('time', FieldType.TIME)
        assert is_valid is False
        assert error_msg is not None
    
    @given(time_str=time_strings())
    @settings(max_examples=50)
    def test_time_format_validation(self, time_str):
        """
        Property: Time strings should follow HH:MM:SS format.
        """
        # Verify the generated time string matches the expected format
        time_pattern = r'^\d{2}:\d{2}:\d{2}$'

        assert re.match(time_pattern, time_str) is not None
        
        # Verify it represents a valid time
        parts = time_str.split(':')
        hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59
    
    @given(
        invalid_suffix=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz',
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_event_fields_without_time_suffix_rejected(self, invalid_suffix):
        """
        Property: Event fields without '_time' suffix should be rejected for TIME type.
        """
        assume(invalid_suffix != 'time')
        
        field_name = f'limit_up_{invalid_suffix}'
        standardizer = FieldStandardizer(NamingRules())
        
        is_valid, _ = standardizer.validate_field_name(field_name, FieldType.TIME)
        assert is_valid is False


# ============================================================================
# Property 4: 持续时间字段命名模式
# **Validates: Requirements 1.5, 12.4**
# ============================================================================

class TestProperty4DurationFieldNamingPattern:
    """
    Property 4: 持续时间字段命名模式
    
    对于任何表示时间跨度或持续天数的字段，字段名应匹配模式 
    `{metric}_days` 或 `{metric}_duration`
    
    **Validates: Requirements 1.5, 12.4**
    """
    
    @given(field_name=valid_duration_field_names())
    @settings(max_examples=100)
    def test_duration_fields_match_pattern(self, field_name):
        """
        Property: All duration field names must match the pattern 
        {metric}_days or {metric}_duration.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # Field name should match the pattern
        duration_pattern = r'^[a-z_]+_(days|duration)$'

        assert re.match(duration_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.DURATION)
        assert is_valid is True
        assert error_msg is None
    
    @given(
        metric=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz_',
            min_size=1,
            max_size=20
        ),
        suffix=st.sampled_from(['days', 'duration'])
    )
    @settings(max_examples=100)
    def test_duration_field_pattern_structure(self, metric, suffix):
        """
        Property: Duration fields must have the structure {metric}_days or {metric}_duration.
        """
        assume(len(metric) > 0 and metric[0] != '_' and metric[-1] != '_')
        assume('__' not in metric)  # No double underscores
        
        field_name = f'{metric}_{suffix}'
        standardizer = FieldStandardizer(NamingRules())
        
        # Should match the pattern
        duration_pattern = r'^[a-z_]+_(days|duration)$'

        assert re.match(duration_pattern, field_name) is not None
        
        # Validation should pass
        is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.DURATION)
        assert is_valid is True
    
    def test_plain_days_or_duration_rejected(self):
        """
        Property: Plain 'days' or 'duration' fields should not be valid for DURATION type.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # 'days' should be invalid
        is_valid, error_msg = standardizer.validate_field_name('days', FieldType.DURATION)
        assert is_valid is False
        assert error_msg is not None
        
        # 'duration' should be invalid
        is_valid, error_msg = standardizer.validate_field_name('duration', FieldType.DURATION)
        assert is_valid is False
        assert error_msg is not None
    
    @given(
        invalid_suffix=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz',
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_duration_fields_with_wrong_suffix_rejected(self, invalid_suffix):
        """
        Property: Duration fields without '_days' or '_duration' suffix should be rejected.
        """
        assume(invalid_suffix not in ['days', 'duration'])
        
        field_name = f'consecutive_{invalid_suffix}'
        standardizer = FieldStandardizer(NamingRules())
        
        is_valid, _ = standardizer.validate_field_name(field_name, FieldType.DURATION)
        assert is_valid is False
    
    @given(
        metric=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz_',
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=50)
    def test_both_days_and_duration_suffixes_valid(self, metric):
        """
        Property: Both '_days' and '_duration' suffixes should be valid for duration fields.
        """
        assume(len(metric) > 0 and metric[0] != '_' and metric[-1] != '_')
        assume('__' not in metric)
        
        standardizer = FieldStandardizer(NamingRules())
        
        # Both should be valid
        field_name_days = f'{metric}_days'
        is_valid_days, _ = standardizer.validate_field_name(field_name_days, FieldType.DURATION)
        assert is_valid_days is True
        
        field_name_duration = f'{metric}_duration'
        is_valid_duration, _ = standardizer.validate_field_name(field_name_duration, FieldType.DURATION)
        assert is_valid_duration is True


# ============================================================================
# Integration Tests: Multiple Field Types in DataFrame
# ============================================================================

class TestDateTimeFieldsInDataFrame:
    """
    Integration tests for date and time fields in DataFrames.
    
    Tests that validate the properties work correctly when standardizing
    complete DataFrames with multiple field types.
    """
    
    @given(
        date_field=valid_date_field_names(),
        event_date_field=valid_event_date_field_names(),
        time_field=valid_time_field_names(),
        duration_field=valid_duration_field_names()
    )
    @settings(max_examples=50)
    def test_dataframe_with_all_date_time_field_types(
        self, date_field, event_date_field, time_field, duration_field
    ):
        """
        Property: A DataFrame with all date/time field types should validate successfully.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # Create a DataFrame with all field types
        df = pd.DataFrame({
            date_field: ['2024-01-01', '2024-01-02'],
            event_date_field: ['2024-01-15', '2024-01-16'],
            time_field: ['09:30:00', '10:00:00'],
            duration_field: [5, 10],
            'timestamp': ['2024-01-01 09:30:00', '2024-01-02 10:00:00']
        })
        
        field_mapping = {
            date_field: FieldType.DATE,
            event_date_field: FieldType.EVENT_DATE,
            time_field: FieldType.TIME,
            duration_field: FieldType.DURATION,
            'timestamp': FieldType.TIMESTAMP
        }
        
        # Should standardize successfully
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # All columns should be preserved
        assert list(result.columns) == list(df.columns)
        
        # Data should be unchanged
        pd.testing.assert_frame_equal(result, df)
    
    @given(
        event_date_fields=st.lists(
            valid_event_date_field_names(),
            min_size=1,
            max_size=5,
            unique=True
        )
    )
    @settings(max_examples=30)
    def test_dataframe_with_multiple_event_dates(self, event_date_fields):
        """
        Property: A DataFrame can have multiple event date fields, 
        all following the {event}_date pattern.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        # Create DataFrame with multiple event date fields
        df_data = {field: ['2024-01-01', '2024-01-02'] for field in event_date_fields}
        df = pd.DataFrame(df_data)
        
        field_mapping = {field: FieldType.EVENT_DATE for field in event_date_fields}
        
        # Should standardize successfully
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # All columns should be preserved
        assert set(result.columns) == set(df.columns)
        
        # All fields should be valid
        for field in event_date_fields:
            is_valid, _ = standardizer.validate_field_name(field, FieldType.EVENT_DATE)
            assert is_valid is True
    
    def test_mixed_valid_and_invalid_fields_raises_error(self):
        """
        Property: A DataFrame with any invalid field name should fail validation.
        """
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'report_date': ['2024-01-15'],
            'invalid_date_field': ['2024-01-20']  # Invalid: doesn't match pattern
        })
        
        field_mapping = {
            'date': FieldType.DATE,
            'report_date': FieldType.EVENT_DATE,
            'invalid_date_field': FieldType.EVENT_DATE  # This should fail
        }
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_dataframe(df, field_mapping)
        
        assert 'invalid_date_field' in str(exc_info.value)


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases for date and time field naming."""
    
    def test_empty_dataframe_with_date_fields(self):
        """Property: Empty DataFrames should validate successfully."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame(columns=['date', 'report_date', 'limit_up_time'])
        field_mapping = {
            'date': FieldType.DATE,
            'report_date': FieldType.EVENT_DATE,
            'limit_up_time': FieldType.TIME
        }
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        assert result.empty
        assert list(result.columns) == list(df.columns)
    
    @given(
        field_name=st.text(
            alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=50)
    def test_uppercase_field_names_rejected(self, field_name):
        """Property: Field names with uppercase letters should be rejected."""
        standardizer = FieldStandardizer(NamingRules())
        
        # All field types should reject uppercase names
        for field_type in [FieldType.DATE, FieldType.EVENT_DATE, FieldType.TIME, FieldType.DURATION]:
            is_valid, _ = standardizer.validate_field_name(field_name, field_type)
            assert is_valid is False
    
    @given(
        special_char=st.sampled_from(['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+'])
    )
    @settings(max_examples=20)
    def test_special_characters_in_field_names_rejected(self, special_char):
        """Property: Field names with special characters should be rejected."""
        standardizer = FieldStandardizer(NamingRules())
        
        field_name = f'report{special_char}date'
        
        is_valid, _ = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
        assert is_valid is False
