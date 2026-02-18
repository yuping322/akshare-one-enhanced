"""
字段标准化器

负责根据命名规范标准化字段名。
"""

import re

import pandas as pd

from .models import FieldType, NamingRules


class FieldStandardizer:
    """字段名标准化器"""
    
    def __init__(self, naming_rules: NamingRules):
        """
        初始化标准化器
        
        Args:
            naming_rules: 命名规则配置
        """
        self.naming_rules = naming_rules
        self._field_type_patterns = self._build_field_type_mapping()
    
    def _build_field_type_mapping(self) -> dict[FieldType, str]:
        """
        构建字段类型到命名模式的映射
        
        Returns:
            字段类型到正则表达式模式的映射字典
        """
        return {
            # 日期/时间类型
            FieldType.DATE: self.naming_rules.date_field_pattern,
            FieldType.EVENT_DATE: self.naming_rules.event_date_field_pattern,
            FieldType.TIMESTAMP: f'^{self.naming_rules.timestamp_field_name}$',
            FieldType.TIME: self.naming_rules.time_field_pattern,
            FieldType.DURATION: self.naming_rules.duration_field_pattern,
            
            # 金额类型
            FieldType.AMOUNT: self.naming_rules.amount_field_pattern,
            FieldType.BALANCE: self.naming_rules.balance_field_pattern,
            FieldType.VALUE: self.naming_rules.value_field_pattern,
            FieldType.NET_FLOW: self.naming_rules.net_flow_pattern,
            
            # 比率类型
            FieldType.RATE: self.naming_rules.rate_field_pattern,
            FieldType.RATIO: self.naming_rules.ratio_field_pattern,
            
            # 标识符类型
            FieldType.SYMBOL: f'^{self.naming_rules.symbol_field_name}$',
            FieldType.NAME: f'^{self.naming_rules.name_field_name}$',
            FieldType.CODE: self.naming_rules.code_field_pattern,
            FieldType.MARKET: f'^{self.naming_rules.market_field_name}$',
            FieldType.RANK: f'^{self.naming_rules.rank_field_name}$',
            
            # 数量类型
            FieldType.COUNT: self.naming_rules.count_field_pattern,
            FieldType.VOLUME: f'^{self.naming_rules.volume_field_name}$',
            FieldType.SHARES: self.naming_rules.shares_field_pattern,
            
            # 特殊类型
            FieldType.BOOLEAN: self.naming_rules.boolean_field_pattern,
            FieldType.TYPE: self.naming_rules.type_field_pattern,
            FieldType.OTHER: r'.*',  # 其他类型接受任何模式
        }
    
    def standardize_field_name(
        self, 
        field_name: str, 
        field_type: FieldType
    ) -> str:
        """
        标准化单个字段名
        
        Args:
            field_name: 原始字段名
            field_type: 字段类型（DATE, AMOUNT, RATIO等）
        
        Returns:
            标准化后的字段名
        
        Raises:
            ValueError: 如果字段名不符合规范
        """
        # 验证字段名
        is_valid, error_message = self.validate_field_name(field_name, field_type)
        
        if not is_valid:
            raise ValueError(
                f"Field name '{field_name}' does not conform to naming rules for type {field_type.value}. "
                f"{error_message}"
            )
        
        # 如果验证通过，返回字段名（已经是标准格式）
        return field_name
    
    def standardize_dataframe(
        self, 
        df: pd.DataFrame, 
        field_mapping: dict[str, FieldType]
    ) -> pd.DataFrame:
        """
        标准化整个DataFrame的字段名
        
        Args:
            df: 原始DataFrame
            field_mapping: 字段名到字段类型的映射
        
        Returns:
            字段名已标准化的DataFrame
        """
        # 创建DataFrame的副本以避免修改原始数据
        result_df = df.copy()
        
        # 验证所有字段名
        for field_name in result_df.columns:
            if field_name in field_mapping:
                field_type = field_mapping[field_name]
                # 验证字段名是否符合规范
                is_valid, error_message = self.validate_field_name(field_name, field_type)
                
                if not is_valid:
                    raise ValueError(
                        f"Field '{field_name}' does not conform to naming rules for type {field_type.value}. "
                        f"{error_message}"
                    )
        
        # 如果所有字段名都有效，返回DataFrame
        return result_df
    
    def validate_field_name(
        self, 
        field_name: str, 
        field_type: FieldType
    ) -> tuple[bool, str | None]:
        """
        验证字段名是否符合规范
        
        Args:
            field_name: 待验证的字段名
            field_type: 字段类型
        
        Returns:
            (是否有效, 错误消息)
        """
        # 获取字段类型对应的命名模式
        pattern = self._field_type_patterns.get(field_type)
        
        if pattern is None:
            return False, f"Unknown field type: {field_type}"
        
        # 验证字段名是否匹配模式
        if re.match(pattern, field_name):
            return True, None
        
        # 生成错误消息
        error_message = self._generate_error_message(field_name, field_type, pattern)
        return False, error_message
    
    def _generate_error_message(
        self, 
        field_name: str, 
        field_type: FieldType, 
        pattern: str
    ) -> str:
        """
        生成详细的错误消息
        
        Args:
            field_name: 字段名
            field_type: 字段类型
            pattern: 期望的命名模式
        
        Returns:
            错误消息
        """
        # 根据字段类型提供具体的建议
        suggestions = {
            FieldType.DATE: "Use 'date' for main date field",
            FieldType.EVENT_DATE: "Use pattern '{event}_date' (e.g., 'report_date', 'announcement_date')",
            FieldType.TIMESTAMP: "Use 'timestamp' for timestamp field",
            FieldType.TIME: "Use pattern '{event}_time' (e.g., 'limit_up_time', 'limit_down_time')",
            FieldType.DURATION: "Use pattern '{metric}_days' or '{metric}_duration' (e.g., 'consecutive_days')",
            FieldType.AMOUNT: "Use pattern '{action}_amount' (e.g., 'buy_amount', 'sell_amount')",
            FieldType.BALANCE: "Use pattern '{category}_balance' (e.g., 'margin_balance', 'total_balance')",
            FieldType.VALUE: "Use pattern '{category}_value' (e.g., 'market_value', 'holdings_value')",
            FieldType.NET_FLOW: "Use pattern '{category}_net_{flow_type}' (e.g., 'main_net_inflow', 'northbound_net_buy')",
            FieldType.RATE: "Use pattern '{metric}_rate' or 'pct_change' or 'turnover_rate'",
            FieldType.RATIO: "Use pattern '{metric}_ratio' (e.g., 'holdings_ratio', 'pledge_ratio')",
            FieldType.SYMBOL: "Use 'symbol' for stock code field",
            FieldType.NAME: "Use 'name' for name field",
            FieldType.CODE: "Use pattern '{entity}_code' (e.g., 'sector_code', 'industry_code')",
            FieldType.MARKET: "Use 'market' for market identifier field",
            FieldType.RANK: "Use 'rank' for ranking field",
            FieldType.COUNT: "Use pattern '{metric}_count' (e.g., 'constituent_count', 'open_count')",
            FieldType.VOLUME: "Use 'volume' for trading volume field",
            FieldType.SHARES: "Use pattern '{category}_shares' (e.g., 'holdings_shares', 'pledge_shares')",
            FieldType.BOOLEAN: "Use pattern 'is_{property}' or 'has_{property}' (e.g., 'is_st', 'has_dividend')",
            FieldType.TYPE: "Use pattern '{entity}_type' or '{entity}_category' (e.g., 'sector_type', 'release_category')",
        }
        
        suggestion = suggestions.get(field_type, f"Expected pattern: {pattern}")
        
        return f"Expected pattern: {pattern}. Suggestion: {suggestion}"
