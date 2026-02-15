"""
字段命名标准化系统

该模块提供字段命名标准化的核心功能，包括：
- 字段类型枚举
- 命名规则配置
- 字段映射配置
- 映射配置管理
- 字段标准化器
- 字段映射器
- 字段别名管理器
- 单位转换器
- 字段验证器
"""

from .models import FieldType, NamingRules, FieldMapping, MappingConfig
from .standardizer import FieldStandardizer
from .field_mapper import FieldMapper
from .alias_manager import FieldAliasManager
from .unit_converter import UnitConverter
from .field_validator import FieldValidator, ValidationResult

__all__ = [
    'FieldType',
    'NamingRules',
    'FieldMapping',
    'MappingConfig',
    'FieldStandardizer',
    'FieldMapper',
    'FieldAliasManager',
    'UnitConverter',
    'FieldValidator',
    'ValidationResult',
]
