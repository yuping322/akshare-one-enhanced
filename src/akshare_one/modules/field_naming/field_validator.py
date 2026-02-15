"""
字段验证器

负责验证字段命名是否符合规范，提供错误消息和纠正建议。
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd

from .models import FieldType, NamingRules


@dataclass
class ValidationResult:
    """字段验证结果"""
    
    field_name: str                    # 字段名
    is_valid: bool                     # 是否有效
    field_type: Optional[FieldType] = None  # 字段类型（如果已知）
    error_message: Optional[str] = None     # 错误消息
    suggested_name: Optional[str] = None    # 建议的字段名
    pattern: Optional[str] = None           # 期望的命名模式


class FieldValidator:
    """字段验证器"""
    
    def __init__(
        self, 
        naming_rules: Optional[NamingRules] = None,
        whitelist: Optional[Set[str]] = None
    ):
        """
        初始化验证器
        
        Args:
            naming_rules: 命名规则配置，如果为None则使用默认规则
            whitelist: 已批准的字段名白名单
        """
        self.naming_rules = naming_rules or NamingRules()
        self.whitelist = whitelist or set()
        self._field_type_patterns = self._build_field_type_mapping()
    
    def _build_field_type_mapping(self) -> Dict[FieldType, str]:
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
    
    def validate_dataframe(
        self, 
        df: pd.DataFrame,
        field_types: Optional[Dict[str, FieldType]] = None
    ) -> Dict[str, ValidationResult]:
        """
        验证DataFrame中所有字段的命名
        
        Args:
            df: 待验证的DataFrame
            field_types: 字段名到字段类型的映射（可选）
        
        Returns:
            字段名到验证结果的映射
        """
        results = {}
        
        for field_name in df.columns:
            # 如果字段在白名单中，直接通过
            if field_name in self.whitelist:
                results[field_name] = ValidationResult(
                    field_name=field_name,
                    is_valid=True
                )
                continue
            
            # 如果提供了字段类型映射，使用指定的类型验证
            if field_types and field_name in field_types:
                field_type = field_types[field_name]
                is_valid, error_msg, suggested_name = self.validate_field_name(
                    field_name, field_type
                )
                pattern = self._field_type_patterns.get(field_type)
                
                results[field_name] = ValidationResult(
                    field_name=field_name,
                    is_valid=is_valid,
                    field_type=field_type,
                    error_message=error_msg,
                    suggested_name=suggested_name,
                    pattern=pattern
                )
            else:
                # 尝试推断字段类型并验证
                inferred_type = self._infer_field_type(field_name)
                
                if inferred_type:
                    is_valid, error_msg, suggested_name = self.validate_field_name(
                        field_name, inferred_type
                    )
                    pattern = self._field_type_patterns.get(inferred_type)
                    
                    results[field_name] = ValidationResult(
                        field_name=field_name,
                        is_valid=is_valid,
                        field_type=inferred_type,
                        error_message=error_msg,
                        suggested_name=suggested_name,
                        pattern=pattern
                    )
                else:
                    # 无法推断类型，标记为未知
                    results[field_name] = ValidationResult(
                        field_name=field_name,
                        is_valid=False,
                        error_message=f"Cannot infer field type for '{field_name}'. "
                                    f"Field name does not match any known pattern.",
                        suggested_name=self._suggest_field_name(field_name)
                    )
        
        return results
    
    def validate_field_name(
        self, 
        field_name: str, 
        field_type: FieldType
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        验证单个字段名是否符合规范
        
        Args:
            field_name: 待验证的字段名
            field_type: 字段类型
        
        Returns:
            (是否有效, 错误消息, 建议的字段名)
        """
        # 如果字段在白名单中，直接通过
        if field_name in self.whitelist:
            return True, None, None
        
        # 获取字段类型对应的命名模式
        pattern = self._field_type_patterns.get(field_type)
        
        if pattern is None:
            return False, f"Unknown field type: {field_type}", None
        
        # 验证字段名是否匹配模式
        if re.match(pattern, field_name):
            return True, None, None
        
        # 生成错误消息和建议
        error_message = self._generate_error_message(field_name, field_type, pattern)
        suggested_name = self._generate_suggestion(field_name, field_type)
        
        return False, error_message, suggested_name
    
    def _infer_field_type(self, field_name: str) -> Optional[FieldType]:
        """
        根据字段名推断字段类型
        
        Args:
            field_name: 字段名
        
        Returns:
            推断的字段类型，如果无法推断则返回None
        """
        # 按优先级顺序检查各种模式
        # 先检查精确匹配
        if field_name == 'date':
            return FieldType.DATE
        if field_name == 'timestamp':
            return FieldType.TIMESTAMP
        if field_name == 'symbol':
            return FieldType.SYMBOL
        if field_name == 'name':
            return FieldType.NAME
        if field_name == 'market':
            return FieldType.MARKET
        if field_name == 'rank':
            return FieldType.RANK
        if field_name == 'volume':
            return FieldType.VOLUME
        
        # 检查模式匹配
        for field_type, pattern in self._field_type_patterns.items():
            if re.match(pattern, field_name):
                return field_type
        
        return None
    
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
        # 根据字段类型提供具体的说明
        type_descriptions = {
            FieldType.DATE: "main date field (YYYY-MM-DD format)",
            FieldType.EVENT_DATE: "event-specific date field",
            FieldType.TIMESTAMP: "timestamp field with timezone",
            FieldType.TIME: "time point within a day (HH:MM:SS format)",
            FieldType.DURATION: "time span or duration in days",
            FieldType.AMOUNT: "transaction amount",
            FieldType.BALANCE: "balance or outstanding amount",
            FieldType.VALUE: "market value or valuation",
            FieldType.NET_FLOW: "net flow of funds",
            FieldType.RATE: "change rate or percentage",
            FieldType.RATIO: "structural ratio or proportion",
            FieldType.SYMBOL: "stock code",
            FieldType.NAME: "name field",
            FieldType.CODE: "sector/industry/concept code",
            FieldType.MARKET: "market identifier",
            FieldType.RANK: "ranking position",
            FieldType.COUNT: "count or quantity",
            FieldType.VOLUME: "trading volume",
            FieldType.SHARES: "number of shares",
            FieldType.BOOLEAN: "boolean flag",
            FieldType.TYPE: "type or category",
        }
        
        description = type_descriptions.get(field_type, "field")
        
        return (
            f"Field '{field_name}' does not conform to naming convention for {description}. "
            f"Expected pattern: {pattern}"
        )
    
    def _generate_suggestion(
        self, 
        field_name: str, 
        field_type: FieldType
    ) -> str:
        """
        生成字段名纠正建议
        
        Args:
            field_name: 原字段名
            field_type: 字段类型
        
        Returns:
            建议的字段名
        """
        # 根据字段类型提供具体的建议
        suggestions = {
            FieldType.DATE: "date",
            FieldType.TIMESTAMP: "timestamp",
            FieldType.SYMBOL: "symbol",
            FieldType.NAME: "name",
            FieldType.MARKET: "market",
            FieldType.RANK: "rank",
            FieldType.VOLUME: "volume",
        }
        
        # 对于有固定名称的字段类型，直接返回标准名称
        if field_type in suggestions:
            return suggestions[field_type]
        
        # 对于其他类型，尝试从字段名中提取关键词并重构
        return self._suggest_field_name(field_name, field_type)
    
    def _suggest_field_name(
        self, 
        field_name: str, 
        field_type: Optional[FieldType] = None
    ) -> str:
        """
        根据字段名和类型生成建议
        
        Args:
            field_name: 原字段名
            field_type: 字段类型（可选）
        
        Returns:
            建议的字段名
        """
        # 转换为小写并替换常见分隔符
        normalized = field_name.lower()
        normalized = re.sub(r'[^\w]+', '_', normalized)
        normalized = normalized.strip('_')
        
        if not field_type:
            return normalized
        
        # 根据字段类型添加适当的后缀
        suffix_map = {
            FieldType.EVENT_DATE: '_date',
            FieldType.TIME: '_time',
            FieldType.DURATION: '_days',
            FieldType.AMOUNT: '_amount',
            FieldType.BALANCE: '_balance',
            FieldType.VALUE: '_value',
            FieldType.RATE: '_rate',
            FieldType.RATIO: '_ratio',
            FieldType.CODE: '_code',
            FieldType.COUNT: '_count',
            FieldType.SHARES: '_shares',
            FieldType.TYPE: '_type',
        }
        
        suffix = suffix_map.get(field_type, '')
        
        # 如果字段名已经有正确的后缀，不重复添加
        if suffix and not normalized.endswith(suffix):
            # 移除可能存在的其他后缀
            for other_suffix in suffix_map.values():
                if normalized.endswith(other_suffix):
                    normalized = normalized[:-len(other_suffix)]
                    break
            normalized = normalized + suffix
        
        # 处理布尔类型的特殊情况
        if field_type == FieldType.BOOLEAN:
            if not (normalized.startswith('is_') or normalized.startswith('has_')):
                normalized = 'is_' + normalized
        
        # 处理净流量类型的特殊情况
        if field_type == FieldType.NET_FLOW:
            if '_net_' not in normalized:
                # 尝试插入 net_
                parts = normalized.split('_')
                if len(parts) >= 2:
                    # 在最后一个词之前插入 net
                    normalized = '_'.join(parts[:-1]) + '_net_' + parts[-1]
        
        return normalized
    
    def add_to_whitelist(self, field_name: str) -> None:
        """
        将字段名添加到白名单
        
        Args:
            field_name: 要添加的字段名
        """
        self.whitelist.add(field_name)
    
    def remove_from_whitelist(self, field_name: str) -> None:
        """
        从白名单中移除字段名
        
        Args:
            field_name: 要移除的字段名
        """
        self.whitelist.discard(field_name)
    
    def load_whitelist(self, whitelist_path: str) -> None:
        """
        从文件加载白名单
        
        Args:
            whitelist_path: 白名单文件路径
        """
        import json
        
        try:
            with open(whitelist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.whitelist = set(data)
                elif isinstance(data, dict) and 'whitelist' in data:
                    self.whitelist = set(data['whitelist'])
                else:
                    raise ValueError("Invalid whitelist file format")
        except FileNotFoundError:
            # 如果文件不存在，使用空白名单
            self.whitelist = set()
    
    def save_whitelist(self, whitelist_path: str) -> None:
        """
        保存白名单到文件
        
        Args:
            whitelist_path: 白名单文件路径
        """
        import json
        
        data = {
            'whitelist': sorted(list(self.whitelist)),
            'count': len(self.whitelist)
        }
        
        with open(whitelist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_validation_summary(
        self, 
        validation_results: Dict[str, ValidationResult]
    ) -> Dict[str, any]:
        """
        生成验证结果摘要
        
        Args:
            validation_results: 验证结果字典
        
        Returns:
            包含统计信息的摘要字典
        """
        total_fields = len(validation_results)
        valid_fields = sum(1 for r in validation_results.values() if r.is_valid)
        invalid_fields = total_fields - valid_fields
        
        # 按字段类型分组统计
        type_stats = {}
        for result in validation_results.values():
            if result.field_type:
                type_name = result.field_type.value
                if type_name not in type_stats:
                    type_stats[type_name] = {'total': 0, 'valid': 0, 'invalid': 0}
                type_stats[type_name]['total'] += 1
                if result.is_valid:
                    type_stats[type_name]['valid'] += 1
                else:
                    type_stats[type_name]['invalid'] += 1
        
        # 收集所有无效字段
        invalid_field_details = [
            {
                'field_name': result.field_name,
                'field_type': result.field_type.value if result.field_type else 'unknown',
                'error_message': result.error_message,
                'suggested_name': result.suggested_name
            }
            for result in validation_results.values()
            if not result.is_valid
        ]
        
        return {
            'total_fields': total_fields,
            'valid_fields': valid_fields,
            'invalid_fields': invalid_fields,
            'validation_rate': valid_fields / total_fields if total_fields > 0 else 0,
            'type_statistics': type_stats,
            'invalid_field_details': invalid_field_details
        }
