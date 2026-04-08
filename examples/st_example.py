#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ST股票数据示例程序

本示例展示如何使用 akshare-one 的ST股票模块获取和分析数据。

依赖：
- pandas

运行方式：
    python st_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#st
"""

# 导入模块
from akshare_one.modules.st import (
    get_st_stocks,
)
from akshare_one.modules.st import STFactory
from akshare_one.modules.exceptions import (
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_st_stocks():
    """场景 1：获取ST股票列表"""
    print("\n" + "=" * 80)
    print("场景 1：获取ST股票列表")
    print("=" * 80)

    try:
        df = get_st_stocks()

        if df.empty:
            print("无ST股票数据返回")
            return

        print(f"\n获取到 {len(df)} 只ST股票")
        print("\n前20只ST股票：")
        print(df.head(20).to_string(index=False))

        if "symbol" in df.columns and "name" in df.columns:
            total_st = len(df)
            print(f"\nST股票总数：{total_st} 只")

        if "st_type" in df.columns:
            st_type_counts = df["st_type"].value_counts()
            print("\nST类型分布：")
            for st_type, count in st_type_counts.items():
                print(f"  {st_type}: {count} 只")

    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有ST股票数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_multi_source():
    """场景 2：使用备用数据源"""
    print("\n" + "=" * 80)
    print("场景 2：使用备用数据源")
    print("=" * 80)

    try:
        available_sources = STFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        default_provider = STFactory.get_provider("eastmoney")
        print(f"\n默认数据源：{default_provider.get_source_name()}")
        print(f"  提供商类型：{type(default_provider).__name__}")

        df = default_provider.get_st_stocks()
        if df.empty:
            print("无数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("ST股票数据示例程序")
    print("=" * 80)

    scenario_1_get_st_stocks()
    scenario_2_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
