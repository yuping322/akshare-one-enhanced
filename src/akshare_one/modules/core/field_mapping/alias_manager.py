"""
字段别名管理器（FieldAliasManager）

管理新旧字段名的别名关系，提供向后兼容性支持。
"""

import logging
import warnings

import pandas as pd

logger = logging.getLogger(__name__)


class FieldAliasManager:
    """字段别名管理器，管理新旧字段名的别名关系"""

    def __init__(self, alias_config: dict[str, str], enable_warnings: bool = True):
        """
        初始化别名管理器

        Args:
            alias_config: 旧字段名到新字段名的映射字典
                         格式：{'old_field_name': 'new_field_name'}
            enable_warnings: 是否启用弃用警告，默认为 True
        """
        self.aliases = alias_config
        self.enable_warnings = enable_warnings
        # 创建反向映射：新字段名到旧字段名列表
        self.reverse_aliases: dict[str, list] = {}
        for old_name, new_name in alias_config.items():
            if new_name not in self.reverse_aliases:
                self.reverse_aliases[new_name] = []
            self.reverse_aliases[new_name].append(old_name)

        logger.info(
            f"Initialized FieldAliasManager with {len(alias_config)} aliases, "
            f"warnings {'enabled' if enable_warnings else 'disabled'}"
        )

    def add_aliases_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        为 DataFrame 添加别名字段

        为标准化后的 DataFrame 添加旧字段名作为别名，指向相同的数据。
        这样用户可以使用旧字段名访问数据，实现向后兼容。

        Args:
            df: 标准化后的 DataFrame

        Returns:
            包含别名字段的 DataFrame（原 DataFrame 的副本）
        """
        # 创建副本以避免修改原始 DataFrame
        df_with_aliases = df.copy()

        added_count = 0
        for new_field in df.columns:
            # 检查是否有旧字段名对应这个新字段名
            if new_field in self.reverse_aliases:
                for old_field in self.reverse_aliases[new_field]:
                    # 添加别名列，指向相同的数据
                    df_with_aliases[old_field] = df_with_aliases[new_field]
                    added_count += 1
                    logger.debug(f"Added alias: {old_field} -> {new_field}")

        if added_count > 0:
            logger.info(f"Added {added_count} alias fields to DataFrame")

        return df_with_aliases

    def resolve_field_access(self, df: pd.DataFrame, field_name: str) -> pd.Series:
        """
        解析字段访问，支持旧字段名

        如果用户访问的是旧字段名，返回对应的新字段数据，
        并可选地发出弃用警告。

        Args:
            df: DataFrame
            field_name: 访问的字段名（可能是旧名称或新名称）

        Returns:
            字段数据

        Raises:
            KeyError: 如果字段不存在（既不是新字段名也不是旧字段名）
        """
        # 如果字段名直接存在，直接返回
        if field_name in df.columns:
            return df[field_name]

        # 检查是否是旧字段名
        if field_name in self.aliases:
            standard_name = self.aliases[field_name]

            # 发出弃用警告
            if self.enable_warnings:
                warnings.warn(
                    f"Field '{field_name}' is deprecated. "
                    f"Use '{standard_name}' instead. "
                    f"Support for '{field_name}' may be removed in future versions.",
                    DeprecationWarning,
                    stacklevel=3,
                )

            # 返回标准字段的数据
            if standard_name in df.columns:
                logger.debug(f"Resolved deprecated field access: {field_name} -> {standard_name}")
                return df[standard_name]
            else:
                raise KeyError(
                    f"Standard field '{standard_name}' not found in DataFrame. "
                    f"Legacy field '{field_name}' maps to '{standard_name}', "
                    f"but '{standard_name}' does not exist."
                )

        # 字段不存在
        raise KeyError(f"Field '{field_name}' not found in DataFrame. Available fields: {list(df.columns)}")

    def get_standard_name(self, legacy_name: str) -> str | None:
        """
        获取旧字段名对应的标准字段名

        Args:
            legacy_name: 旧字段名

        Returns:
            标准字段名，如果不存在则返回 None
        """
        return self.aliases.get(legacy_name)

    def is_legacy_field(self, field_name: str) -> bool:
        """
        检查字段名是否是旧字段名

        Args:
            field_name: 字段名

        Returns:
            如果是旧字段名返回 True，否则返回 False
        """
        return field_name in self.aliases

    def get_all_aliases(self) -> dict[str, str]:
        """
        获取所有别名映射

        Returns:
            旧字段名到新字段名的映射字典
        """
        return self.aliases.copy()

    def add_alias(self, old_name: str, new_name: str) -> None:
        """
        添加新的别名映射

        Args:
            old_name: 旧字段名
            new_name: 新字段名
        """
        self.aliases[old_name] = new_name

        # 更新反向映射
        if new_name not in self.reverse_aliases:
            self.reverse_aliases[new_name] = []
        if old_name not in self.reverse_aliases[new_name]:
            self.reverse_aliases[new_name].append(old_name)

        logger.info(f"Added alias mapping: {old_name} -> {new_name}")

    def remove_alias(self, old_name: str) -> bool:
        """
        移除别名映射

        Args:
            old_name: 要移除的旧字段名

        Returns:
            如果成功移除返回 True，如果别名不存在返回 False
        """
        if old_name in self.aliases:
            new_name = self.aliases[old_name]
            del self.aliases[old_name]

            # 更新反向映射
            if new_name in self.reverse_aliases:
                self.reverse_aliases[new_name].remove(old_name)
                if not self.reverse_aliases[new_name]:
                    del self.reverse_aliases[new_name]

            logger.info(f"Removed alias mapping: {old_name}")
            return True

        return False
