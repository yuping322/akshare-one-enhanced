#!/usr/bin/env python3
"""
字段格式化器
提供各种字段格式的标准化转换功能
"""

import re
from enum import Enum
from typing import Any


class StockCodeFormat(Enum):
    """股票代码格式"""

    PURE_NUMERIC = "pure_numeric"  # 纯数字，如 "000001"
    WITH_SUFFIX = "with_suffix"  # 带后缀，如 "000001.SZ"
    WITH_PREFIX = "with_prefix"  # 带前缀，如 "sz000001"


class DateFormat(Enum):
    """日期格式"""

    YYYYMMDD = "YYYYMMDD"  # "20240101"
    YYYY_MM_DD = "YYYY-MM-DD"  # "2024-01-01"
    YYYY_MM_DD_HH_MM_SS = "YYYY-MM-DD HH:MM:SS"  # "2024-01-01 12:34:56"
    YYYYMM = "YYYYMM"  # "202401"
    YYYY_MM = "YYYY-MM"  # "2024-01"


class FieldFormatter:
    """字段格式化器 - 核心工具类"""

    # 股票代码后缀映射
    MARKET_SUFFIX = {
        "sh": ["SH", "sh", ".SH", ".sh", "中", "沪", "上证"],
        "sz": ["SZ", "sz", ".SZ", ".sz", "深", "深证"],
        "bj": ["BJ", "bj", ".BJ", ".bj", "北", "北证", "京"],
    }

    # 股票代码前缀映射
    MARKET_PREFIX = {
        "sh": ["sh", "SH", "上证", "沪"],
        "sz": ["sz", "SZ", "深证", "深"],
        "bj": ["bj", "BJ", "北证", "京", "首"],
    }

    # 中文字符到市场的映射
    CN_MARKET_MAP = {
        "上证": "sh",
        "沪": "sh",
        "中": "sh",
        "沪市": "sh",
        "深证": "sz",
        "深": "sz",
        "深市": "sz",
        "北证": "bj",
        "北": "bj",
        "京": "bj",
        "首": "bj",
        "北交所": "bj",
    }

    @staticmethod
    def normalize_stock_code(
        code: str | int | None,
        target_format: StockCodeFormat = StockCodeFormat.PURE_NUMERIC,
        default_market: str = "auto",
    ) -> str | None:
        """
        标准化股票代码格式

        Args:
            code: 股票代码
            target_format: 目标格式
            default_market: 默认市场（当无法推断时使用）

        Returns:
            标准化后的股票代码
        """
        if code is None:
            return None

        code_str = str(code).strip()
        if not code_str:
            return None

        # 1. 提取纯数字部分和市场标识
        numeric_part = ""
        market = None

        code_str_clean = code_str

        # 检查是否有后缀（按长度排序，先匹配长的）
        all_suffixes = []
        for mkt, suffixes in FieldFormatter.MARKET_SUFFIX.items():
            for suffix in suffixes:
                all_suffixes.append((mkt, suffix))

        all_suffixes.sort(key=lambda x: len(x[1]), reverse=True)

        for mkt, suffix in all_suffixes:
            if code_str_clean.endswith(suffix):
                numeric_part = code_str_clean[: -len(suffix)]
                market = mkt
                break

        # 检查是否有前缀
        if not market:
            all_prefixes = []
            for mkt, prefixes in FieldFormatter.MARKET_PREFIX.items():
                for prefix in prefixes:
                    all_prefixes.append((mkt, prefix))

            all_prefixes.sort(key=lambda x: len(x[1]), reverse=True)

            for mkt, prefix in all_prefixes:
                if code_str_clean.startswith(prefix):
                    numeric_part = code_str_clean[len(prefix) :]
                    market = mkt
                    break

        # 如果都没有，提取数字部分
        if not market:
            numeric_match = re.search(r"(\d+)", code_str_clean)
            if numeric_match:
                numeric_part = numeric_match.group(1)
                # 尝试根据代码长度推断市场
                if default_market == "auto":
                    if len(numeric_part) == 6:
                        if numeric_part.startswith("6"):
                            market = "sh"
                        elif numeric_part.startswith("0") or numeric_part.startswith("3"):
                            market = "sz"
                        elif (
                            numeric_part.startswith("8") or numeric_part.startswith("4") or numeric_part.startswith("9")
                        ):
                            market = "bj"
                else:
                    market = default_market

        if not numeric_part:
            return code_str

        # 只保留数字
        numeric_part = re.sub(r"[^\d]", "", numeric_part)

        # 补全到6位
        numeric_part = numeric_part.zfill(6)

        # 2. 按目标格式输出
        if target_format == StockCodeFormat.PURE_NUMERIC:
            return numeric_part
        elif target_format == StockCodeFormat.WITH_SUFFIX:
            if market:
                suffix = f".{market.upper()}"
                return f"{numeric_part}{suffix}"
            return numeric_part
        elif target_format == StockCodeFormat.WITH_PREFIX:
            if market:
                return f"{market.lower()}{numeric_part}"
            return numeric_part

        return numeric_part

    @staticmethod
    def normalize_date(date_str: str | int | None, target_format: DateFormat = DateFormat.YYYY_MM_DD) -> str | None:
        """
        标准化日期格式

        Args:
            date_str: 日期字符串
            target_format: 目标格式

        Returns:
            标准化后的日期字符串
        """
        if date_str is None:
            return None

        date_str = str(date_str).strip()
        if not date_str or date_str.lower() in ["nan", "nat", "none", "null"]:
            return None

        # 处理常见格式
        year = month = day = hour = minute = second = None

        # 优先手动解析中文日期格式（避免 pandas 错误解析）
        # 格式: 2024年1月1日, 2024年01月01日
        cn_date_match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
        if cn_date_match:
            year = int(cn_date_match.group(1))
            month = int(cn_date_match.group(2))
            day = int(cn_date_match.group(3))
        else:
            # 尝试用 pandas 解析（如果可用）
            try:
                import pandas as pd

                dt = pd.to_datetime(date_str, errors="coerce", dayfirst=False)
                if pd.notna(dt):
                    year = dt.year
                    month = dt.month
                    day = dt.day
                    hour = dt.hour
                    minute = dt.minute
                    second = dt.second
            except Exception:
                pass

        # 如果都解析失败，手动解析
        if year is None:
            # 提取数字部分
            digits = re.findall(r"\d+", date_str)
            if not digits:
                return date_str

            # 组合数字
            combined = "".join(digits)

            # 根据长度解析
            if len(combined) >= 8:
                year = int(combined[0:4])
                month = int(combined[4:6])
                day = int(combined[6:8])
                if len(combined) >= 14:
                    hour = int(combined[8:10])
                    minute = int(combined[10:12])
                    second = int(combined[12:14])
            elif len(combined) == 6:
                year = int(combined[0:4])
                month = int(combined[4:6])
            elif len(combined) == 4:
                year = int(combined)
                month = 1
                day = 1

        if year is None:
            return date_str

        # 验证日期合理性
        if month is None or not (1 <= month <= 12):
            month = 1
        if day is None or not (1 <= day <= 31):
            day = 1

        # 生成目标格式
        if target_format == DateFormat.YYYYMMDD and year and month and day:
            return f"{year:04d}{month:02d}{day:02d}"
        elif target_format == DateFormat.YYYY_MM_DD and year and month and day:
            return f"{year:04d}-{month:02d}-{day:02d}"
        elif target_format == DateFormat.YYYY_MM_DD_HH_MM_SS and year and month and day:
            if hour is not None:
                return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute or 0:02d}:{second or 0:02d}"
            return f"{year:04d}-{month:02d}-{day:02d} 00:00:00"
        elif target_format == DateFormat.YYYYMM and year and month:
            return f"{year:04d}{month:02d}"
        elif target_format == DateFormat.YYYY_MM and year and month:
            return f"{year:04d}-{month:02d}"

        return date_str

    @staticmethod
    def normalize_float(value: str | float | int | None) -> float | None:
        """标准化浮点数"""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        value_str = str(value).strip()
        if not value_str or value_str == "-" or value_str.lower() in ["nan", "none", "null"]:
            return None

        # 处理百分比
        is_percent = False
        if "%" in value_str:
            is_percent = True
            value_str = value_str.replace("%", "")

        # 清理字符串，保留数字、小数点、负号、逗号
        value_str = re.sub(r"[^\d\.\-\+]", "", value_str)

        # 处理千位分隔符 - 先移除所有逗号（假设都是千位分隔符）
        # 这样可以确保 1,234.56 变成 1234.56
        if "," in value_str and "." in value_str:
            # 同时有逗号和小数点，逗号应该是千位分隔符
            value_str = value_str.replace(",", "")
        elif "," in value_str:
            # 只有逗号，看后面的长度
            parts = value_str.split(",")
            if len(parts) > 2:
                # 多个逗号，千位分隔符
                value_str = value_str.replace(",", "")
            elif len(parts) == 2:
                # 一个逗号
                if len(parts[1]) == 3:
                    # 千位分隔符
                    value_str = value_str.replace(",", "")
                else:
                    # 小数点
                    value_str = value_str.replace(",", ".")

        try:
            result = float(value_str)
            if is_percent:
                result = result / 100.0
            return result
        except (ValueError, TypeError):
            return None

    @staticmethod
    def normalize_int(value: str | float | int | None) -> int | None:
        """标准化整数"""
        if value is None:
            return None

        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(round(value))

        value_str = str(value).strip()
        if not value_str or value_str == "-" or value_str.lower() in ["nan", "none", "null"]:
            return None

        # 先尝试作为浮点数解析，再取整
        float_val = FieldFormatter.normalize_float(value_str)
        if float_val is not None:
            return int(round(float_val))

        return None

    @staticmethod
    def normalize_boolean(value: Any) -> bool | None:
        """标准化布尔值"""
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        value_str = str(value).strip().lower()
        true_values = ["true", "yes", "1", "t", "y", "是", "对", "真"]
        false_values = ["false", "no", "0", "f", "n", "否", "错", "假"]

        if value_str in true_values:
            return True
        elif value_str in false_values:
            return False
        else:
            return None


# 方便的直接访问接口
def format_stock_code(code: str, format_type: str = "pure") -> str | None:
    """格式化股票代码的快捷方式"""
    format_map = {
        "pure": StockCodeFormat.PURE_NUMERIC,
        "numeric": StockCodeFormat.PURE_NUMERIC,
        "suffix": StockCodeFormat.WITH_SUFFIX,
        "with_suffix": StockCodeFormat.WITH_SUFFIX,
        "prefix": StockCodeFormat.WITH_PREFIX,
        "with_prefix": StockCodeFormat.WITH_PREFIX,
    }
    target_format = format_map.get(format_type, StockCodeFormat.PURE_NUMERIC)
    return FieldFormatter.normalize_stock_code(code, target_format)


def format_date(date_str: str, format_type: str = "ymd") -> str | None:
    """格式化日期的快捷方式"""
    format_map = {
        "ymd": DateFormat.YYYY_MM_DD,
        "yyyy-mm-dd": DateFormat.YYYY_MM_DD,
        "yyyymmdd": DateFormat.YYYYMMDD,
        "ym": DateFormat.YYYYMM,
        "yyyy-mm": DateFormat.YYYY_MM,
        "ymd_hms": DateFormat.YYYY_MM_DD_HH_MM_SS,
    }
    target_format = format_map.get(format_type, DateFormat.YYYY_MM_DD)
    return FieldFormatter.normalize_date(date_str, target_format)


def format_float(value: Any) -> float | None:
    """格式化浮点数的快捷方式"""
    return FieldFormatter.normalize_float(value)


def format_int(value: Any) -> int | None:
    """格式化整数的快捷方式"""
    return FieldFormatter.normalize_int(value)


def format_boolean(value: Any) -> bool | None:
    """格式化布尔值的快捷方式"""
    return FieldFormatter.normalize_boolean(value)
