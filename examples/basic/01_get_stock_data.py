#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 1：获取股票历史数据

本示例展示如何使用 akshare-one 获取股票历史K线数据，包括：
- 获取日线数据
- 获取分钟线数据
- 获取周线/月线数据
- 复权处理

运行方式：
    python examples/basic/01_get_stock_data.py
"""

import pandas as pd
from akshare_one import get_hist_data, get_hist_data_multi_source


def example_daily_data():
    """示例1：获取日线数据"""
    print("\n" + "=" * 60)
    print("示例1：获取股票日线数据")
    print("=" * 60)

    # 获取股票日线数据（不复权）
    df = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="none",
        source="eastmoney_direct"
    )

    print(f"\n获取到 {len(df)} 条日线数据")
    print("\n最近5天的数据：")
    print(df.head().to_string(index=False))

    # 数据包含以下字段：
    # - timestamp: 时间戳
    # - open: 开盘价
    # - high: 最高价
    # - low: 最低价
    # - close: 收盘价
    # - volume: 成交量


def example_minute_data():
    """示例2：获取分钟线数据"""
    print("\n" + "=" * 60)
    print("示例2：获取股票分钟线数据")
    print("=" * 60)

    # 获取5分钟K线数据
    df = get_hist_data(
        symbol="000001",
        interval="minute",
        interval_multiplier=5,
        start_date="2024-12-01",
        end_date="2024-12-31",
        adjust="none",
        source="eastmoney_direct"
    )

    print(f"\n获取到 {len(df)} 条5分钟数据")
    print("\n最近10条数据：")
    print(df.head(10).to_string(index=False))


def example_weekly_monthly():
    """示例3：获取周线和月线数据"""
    print("\n" + "=" * 60)
    print("示例3：获取周线和月线数据")
    print("=" * 60)

    # 获取周线数据
    df_week = get_hist_data(
        symbol="600519",
        interval="week",
        start_date="2024-01-01",
        end_date="2024-12-31",
        source="eastmoney_direct"
    )

    print(f"\n周线数据：{len(df_week)} 条")
    print(df_week.head().to_string(index=False))

    # 获取月线数据
    df_month = get_hist_data(
        symbol="600519",
        interval="month",
        start_date="2024-01-01",
        end_date="2024-12-31",
        source="eastmoney_direct"
    )

    print(f"\n月线数据：{len(df_month)} 条")
    print(df_month.head().to_string(index=False))


def example_adjusted_data():
    """示例4：复权数据处理"""
    print("\n" + "=" * 60)
    print("示例4：复权数据处理")
    print("=" * 60)

    # 不复权
    df_none = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="none",
        source="eastmoney_direct"
    )

    # 前复权
    df_qfq = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="qfq",
        source="eastmoney_direct"
    )

    # 后复权
    df_hfq = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="hfq",
        source="eastmoney_direct"
    )

    print(f"\n不复权数据：{len(df_none)} 条")
    print(f"前复权数据：{len(df_qfq)} 条")
    print(f"后复权数据：{len(df_hfq)} 条")

    # 对比复权前后的价格差异
    if len(df_none) > 0 and len(df_qfq) > 0:
        print("\n价格对比（最近一天）：")
        print(f"  不复权收盘价: {df_none.iloc[-1]['close']:.2f}")
        print(f"  前复权收盘价: {df_qfq.iloc[-1]['close']:.2f}")
        print(f"  后复权收盘价: {df_hfq.iloc[-1]['close']:.2f}")


def example_multi_source():
    """示例5：多数据源自动切换"""
    print("\n" + "=" * 60)
    print("示例5：多数据源自动切换")
    print("=" * 60)

    # 使用多数据源，自动切换
    # 当第一个数据源失败时，会自动尝试下一个
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["eastmoney_direct", "eastmoney", "sina"]
    )

    print(f"\n获取到 {len(df)} 条数据")
    print("\n数据预览：")
    print(df.head().to_string(index=False))


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 股票数据获取示例")
    print("=" * 60)

    # 运行所有示例
    example_daily_data()
    example_minute_data()
    example_weekly_monthly()
    example_adjusted_data()
    example_multi_source()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()