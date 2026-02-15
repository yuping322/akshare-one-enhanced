"""
字段命名标准化系统的核心数据模型

包含字段类型枚举、命名规则、字段映射和映射配置等数据类。
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class FieldType(Enum):
    """字段类型枚举"""
    
    # 日期/时间类型
    DATE = 'date'              # 日期字段
    TIMESTAMP = 'timestamp'    # 时间戳字段
    EVENT_DATE = 'event_date'  # 事件日期
    TIME = 'time'              # 时间字段
    DURATION = 'duration'      # 持续时间
    
    # 金额类型
    AMOUNT = 'amount'          # 金额
    BALANCE = 'balance'        # 余额
    VALUE = 'value'            # 市值
    NET_FLOW = 'net_flow'      # 净流量
    
    # 比率类型
    RATE = 'rate'              # 变化率
    RATIO = 'ratio'            # 结构比例
    
    # 标识符类型
    SYMBOL = 'symbol'          # 股票代码
    NAME = 'name'              # 名称
    CODE = 'code'              # 代码
    MARKET = 'market'          # 市场
    RANK = 'rank'              # 排名
    
    # 数量类型
    COUNT = 'count'            # 计数
    VOLUME = 'volume'          # 成交量
    SHARES = 'shares'          # 股份
    
    # 特殊类型
    BOOLEAN = 'boolean'        # 布尔标志
    TYPE = 'type'              # 类型/类别
    OTHER = 'other'            # 其他


@dataclass
class NamingRules:
    """字段命名规则配置"""
    
    # 日期/时间字段规则
    date_field_pattern: str = r'^date$'
    event_date_field_pattern: str = r'^[a-z_]+_date$'
    timestamp_field_name: str = 'timestamp'
    time_field_pattern: str = r'^[a-z_]+_time$'
    duration_field_pattern: str = r'^[a-z_]+_(days|duration)$'
    
    # 金额字段规则
    amount_field_pattern: str = r'^[a-z_]+_amount$'
    balance_field_pattern: str = r'^[a-z_]+_balance$'
    value_field_pattern: str = r'^[a-z_]+_value$'
    net_flow_pattern: str = r'^[a-z_]+_net_(inflow|outflow|buy|sell)$'
    
    # 比率字段规则
    rate_field_pattern: str = r'^([a-z_]+_rate|pct_change|turnover_rate)$'
    ratio_field_pattern: str = r'^[a-z_]+_ratio$'
    
    # 标识符字段规则
    symbol_field_name: str = 'symbol'
    name_field_name: str = 'name'
    code_field_pattern: str = r'^[a-z_]+_code$'
    market_field_name: str = 'market'
    rank_field_name: str = 'rank'
    
    # 计数字段规则
    count_field_pattern: str = r'^[a-z_]+_count$'
    
    # 股份/成交量字段规则
    volume_field_name: str = 'volume'
    shares_field_pattern: str = r'^[a-z_]+_shares$'
    
    # 特殊字段规则
    boolean_field_pattern: str = r'^(is|has)_[a-z_]+$'
    type_field_pattern: str = r'^[a-z_]+_(type|category)$'
    
    def _get_pattern_for_type(self, field_type: FieldType) -> str:
        """获取字段类型对应的命名模式"""
        pattern_map = {
            FieldType.DATE: self.date_field_pattern,
            FieldType.EVENT_DATE: self.event_date_field_pattern,
            FieldType.TIMESTAMP: f'^{self.timestamp_field_name}$',
            FieldType.TIME: self.time_field_pattern,
            FieldType.DURATION: self.duration_field_pattern,
            FieldType.AMOUNT: self.amount_field_pattern,
            FieldType.BALANCE: self.balance_field_pattern,
            FieldType.VALUE: self.value_field_pattern,
            FieldType.NET_FLOW: self.net_flow_pattern,
            FieldType.RATE: self.rate_field_pattern,
            FieldType.RATIO: self.ratio_field_pattern,
            FieldType.SYMBOL: f'^{self.symbol_field_name}$',
            FieldType.NAME: f'^{self.name_field_name}$',
            FieldType.CODE: self.code_field_pattern,
            FieldType.MARKET: f'^{self.market_field_name}$',
            FieldType.RANK: f'^{self.rank_field_name}$',
            FieldType.COUNT: self.count_field_pattern,
            FieldType.VOLUME: f'^{self.volume_field_name}$',
            FieldType.SHARES: self.shares_field_pattern,
            FieldType.BOOLEAN: self.boolean_field_pattern,
            FieldType.TYPE: self.type_field_pattern,
            FieldType.OTHER: r'.*',  # 其他类型接受任何模式
        }
        return pattern_map.get(field_type, r'.*')
    
    def validate_field_name(
        self, 
        field_name: str, 
        field_type: FieldType
    ) -> bool:
        """
        验证字段名是否符合规则
        
        Args:
            field_name: 待验证的字段名
            field_type: 字段类型
        
        Returns:
            是否符合规则
        """
        pattern = self._get_pattern_for_type(field_type)
        return bool(re.match(pattern, field_name))


@dataclass
class FieldMapping:
    """字段映射配置"""
    
    source_field: str          # 源字段名
    standard_field: str        # 标准字段名
    field_type: FieldType      # 字段类型
    source_unit: Optional[str] = None  # 源单位（金额字段）
    target_unit: str = 'yuan'  # 目标单位
    transform: Optional[Callable] = None  # 自定义转换函数
    description: str = ''      # 映射说明
    
    def apply(self, value: Any) -> Any:
        """
        应用映射转换
        
        Args:
            value: 原始值
        
        Returns:
            转换后的值
        """
        if self.transform:
            return self.transform(value)
        return value


@dataclass
class MappingConfig:
    """模块级别的映射配置"""
    
    source: str                # 数据源名称
    module: str                # 模块名称
    mappings: List[FieldMapping] = field(default_factory=list)  # 字段映射列表
    version: str = '1.0'       # 配置版本
    last_updated: str = ''     # 最后更新时间
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            字典表示
        """
        return {
            'source': self.source,
            'module': self.module,
            'version': self.version,
            'last_updated': self.last_updated,
            'mappings': [
                {
                    'source_field': m.source_field,
                    'standard_field': m.standard_field,
                    'field_type': m.field_type.value,
                    'source_unit': m.source_unit,
                    'target_unit': m.target_unit,
                    'description': m.description
                }
                for m in self.mappings
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MappingConfig':
        """
        从字典创建配置
        
        Args:
            data: 字典数据
        
        Returns:
            MappingConfig 实例
        """
        mappings = [
            FieldMapping(
                source_field=m['source_field'],
                standard_field=m['standard_field'],
                field_type=FieldType(m['field_type']),
                source_unit=m.get('source_unit'),
                target_unit=m.get('target_unit', 'yuan'),
                description=m.get('description', '')
            )
            for m in data.get('mappings', [])
        ]
        return cls(
            source=data['source'],
            module=data['module'],
            mappings=mappings,
            version=data.get('version', '1.0'),
            last_updated=data.get('last_updated', '')
        )
