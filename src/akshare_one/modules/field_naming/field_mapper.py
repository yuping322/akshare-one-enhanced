"""
字段映射器（FieldMapper）

管理源数据字段到标准字段的映射，支持从配置文件加载映射规则。
"""

import json
import logging
from pathlib import Path

import pandas as pd

from .models import FieldMapping, MappingConfig

logger = logging.getLogger(__name__)


class FieldMapper:
    """字段映射器，管理源数据字段到标准字段的映射"""
    
    def __init__(self, config_path: str | None = None):
        """
        初始化映射器
        
        Args:
            config_path: 映射配置文件路径或目录路径。
                        如果为 None，使用默认的 field_mappings 目录
        """
        self.config_path = config_path
        self.mappings: dict[str, dict[str, MappingConfig]] = {}
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """
        加载映射配置
        
        从配置文件或目录加载所有映射配置。
        配置文件格式：{source}_{module}.json
        """
        if self.config_path is None:
            # 使用默认配置目录
            config_dir = Path(__file__).parent.parent / 'field_mappings'
        else:
            config_dir = Path(self.config_path)
        
        if not config_dir.exists():
            logger.warning(
                f"Mapping configuration directory not found: {config_dir}. "
                f"No mappings will be loaded."
            )
            return
        
        if config_dir.is_file():
            # 单个配置文件
            self._load_single_config(config_dir)
        else:
            # 目录，加载所有 JSON 文件
            for config_file in config_dir.glob('*.json'):
                self._load_single_config(config_file)
        
        logger.info(f"Loaded {len(self.mappings)} mapping configurations")
    
    def _load_single_config(self, config_file: Path) -> None:
        """
        加载单个配置文件
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, encoding='utf-8') as f:
                data = json.load(f)
            
            config = MappingConfig.from_dict(data)
            
            # 存储到嵌套字典：mappings[source][module] = config
            if config.source not in self.mappings:
                self.mappings[config.source] = {}
            
            self.mappings[config.source][config.module] = config
            
            logger.debug(
                f"Loaded mapping config for {config.source}/{config.module} "
                f"from {config_file.name}"
            )
        
        except Exception as e:
            logger.error(
                f"Failed to load mapping config from {config_file}: {e}"
            )
    
    def map_fields(
        self, 
        df: pd.DataFrame, 
        source: str, 
        module: str
    ) -> pd.DataFrame:
        """
        将源数据字段映射到标准字段
        
        Args:
            df: 原始 DataFrame
            source: 数据源名称（如 'eastmoney'）
            module: 模块名称（如 'fundflow'）
        
        Returns:
            字段已映射的 DataFrame
        """
        # 获取映射配置
        config = self.mappings.get(source, {}).get(module)
        
        if config is None:
            logger.warning(
                f"No mapping configuration found for {source}/{module}. "
                f"Returning DataFrame unchanged."
            )
            return df
        
        # 创建字段名映射字典
        rename_dict = {}
        for mapping in config.mappings:
            if mapping.source_field in df.columns:
                rename_dict[mapping.source_field] = mapping.standard_field
                logger.debug(
                    f"Mapping field: {mapping.source_field} -> "
                    f"{mapping.standard_field} ({mapping.field_type.value})"
                )
        
        # 应用重命名
        if rename_dict:
            df = df.rename(columns=rename_dict)
            logger.info(
                f"Mapped {len(rename_dict)} fields for {source}/{module}"
            )
        else:
            logger.warning(
                f"No matching fields found to map for {source}/{module}"
            )
        
        return df
    
    def get_mapping(
        self, 
        source: str, 
        module: str, 
        source_field: str
    ) -> FieldMapping | None:
        """
        获取特定字段的映射配置
        
        Args:
            source: 数据源名称
            module: 模块名称
            source_field: 源字段名
        
        Returns:
            字段映射配置，如果不存在则返回 None
        """
        config = self.mappings.get(source, {}).get(module)
        
        if config is None:
            return None
        
        for mapping in config.mappings:
            if mapping.source_field == source_field:
                return mapping
        
        return None
    
    def add_mapping(
        self, 
        source: str, 
        module: str, 
        mapping: FieldMapping
    ) -> None:
        """
        添加新的字段映射
        
        Args:
            source: 数据源名称
            module: 模块名称
            mapping: 字段映射配置
        """
        # 确保配置存在
        if source not in self.mappings:
            self.mappings[source] = {}
        
        if module not in self.mappings[source]:
            self.mappings[source][module] = MappingConfig(
                source=source,
                module=module,
                mappings=[]
            )
        
        # 检查是否已存在相同的源字段映射
        config = self.mappings[source][module]
        for i, existing_mapping in enumerate(config.mappings):
            if existing_mapping.source_field == mapping.source_field:
                # 替换现有映射
                config.mappings[i] = mapping
                logger.info(
                    f"Updated mapping for {source}/{module}: "
                    f"{mapping.source_field} -> {mapping.standard_field}"
                )
                return
        
        # 添加新映射
        config.mappings.append(mapping)
        logger.info(
            f"Added mapping for {source}/{module}: "
            f"{mapping.source_field} -> {mapping.standard_field}"
        )
