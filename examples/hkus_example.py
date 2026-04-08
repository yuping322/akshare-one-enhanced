#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港美股数据示例程序

本示例展示如何使用 akshare-one 的港美股模块获取和分析数据。

依赖：
- pandas

运行方式：
    python hkus_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#hkus
"""

import pandas as pd

from akshare_one.modules.hkus import (
    get_hk_stocks,
    get_us_stocks,
)
from akshare_one.modules.hkus import HKUSFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_hk_stock_list():
    """场景 1：获取港股列表"""
    print("\n" + "=" * 80)
    print("场景 1：获取港股列表")
    print("=" * 80)

    try:
        print("\n查询所有港股股票列表...")

        df = get_hk_stocks()

        if df.empty:
            print("无港股数据返回")
            return

        print(f"\n获取到 {len(df)} 只港股")

        display_columns = [
            col for col in ["symbol", "name", "close_price", "pct_change", "turnover"] if col in df.columns
        ]
        if display_columns:
            print("\n前10只港股：")
            print(df.head(10)[display_columns].to_string(index=False))
        else:
            print("\n前10只港股：")
            print(df.head(10).to_string(index=False))

        if "close_price" in df.columns:
            valid_prices = df[df["close_price"].notna()]["close_price"]
            if len(valid_prices) > 0:
                print(f"\n价格统计：")
                print(f"  最高价：{valid_prices.max():.2f}")
                print(f"  最低价：{valid_prices.min():.2f}")
                print(f"  平均价：{valid_prices.mean():.2f}")

    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：数据源可能暂时没有数据，请稍后重试")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_get_us_stock_list():
    """场景 2：获取美股列表"""
    print("\n" + "=" * 80)
    print("场景 2：获取美股列表")
    print("=" * 80)

    try:
        print("\n查询所有美股股票列表...")

        df = get_us_stocks()

        if df.empty:
            print("无美股数据返回")
            return

        print(f"\n获取到 {len(df)} 只美股")

        display_columns = [
            col for col in ["symbol", "name", "close_price", "pct_change", "turnover"] if col in df.columns
        ]
        if display_columns:
            print("\n前10只美股：")
            print(df.head(10)[display_columns].to_string(index=False))
        else:
            print("\n前10只美股：")
            print(df.head(10).to_string(index=False))

        if "pct_change" in df.columns:
            valid_changes = df[df["pct_change"].notna()]["pct_change"]
            if len(valid_changes) > 0:
                print(f"\n涨跌幅统计：")
                print(f"  最大涨幅：{valid_changes.max():.2f}%")
                print(f"  最大跌幅：{valid_changes.min():.2f}%")
                print(f"  平均涨跌幅：{valid_changes.mean():.2f}%")

    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：数据源可能暂时没有数据，请稍后重试")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_multi_source_example():
    """场景 3：使用备用数据源"""
    print("\n" + "=" * 80)
    print("场景 3：使用备用数据源")
    print("=" * 80)

    try:
        available_sources = HKUSFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        if not available_sources:
            print("没有可用的数据源")
            return

        source = available_sources[0] if available_sources else None
        if source:
            print(f"\n使用 {source} 数据源：")
            provider = HKUSFactory.get_provider(source)
            print(f"  提供商类型：{type(provider).__name__}")
            print(f"  数据源名称：{provider.get_source_name()}")

            print("\n尝试获取港股数据...")
            df = provider.get_hk_stocks()

            if df.empty:
                print("无港股数据返回")
            else:
                print(f"获取到 {len(df)} 条记录")
                print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("港美股数据示例程序")
    print("=" * 80)

    scenario_1_get_hk_stock_list()
    scenario_2_get_us_stock_list()
    scenario_3_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
