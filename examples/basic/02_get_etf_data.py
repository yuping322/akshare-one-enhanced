#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 2：获取ETF数据

本示例展示如何使用 akshare-one 获取ETF基金数据，包括：
- 获取ETF历史数据
- 获取ETF实时行情
- 获取ETF基本信息

运行方式：
    python examples/basic/02_get_etf_data.py
"""

import pandas as pd
from akshare_one import get_hist_data, get_realtime_data
from akshare_one.modules.etf import ETFFactory


def example_etf_hist_data():
    """示例1：获取ETF历史数据"""
    print("\n" + "=" * 60)
    print("示例1：获取ETF历史数据")
    print("=" * 60)

    # 获取沪深300ETF历史数据
    df = get_hist_data(
        symbol="510300",  # 沪深300ETF
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        adjust="none",
        source="eastmoney_direct",
    )

    print(f"\n获取到 {len(df)} 条ETF日线数据")
    print("\n最近5天的数据：")
    print(df.head().to_string(index=False))


def example_etf_realtime():
    """示例2：获取ETF实时行情"""
    print("\n" + "=" * 60)
    print("示例2：获取ETF实时行情")
    print("=" * 60)

    # 获取单个ETF实时行情
    df = get_realtime_data(symbol="510300", source="eastmoney_direct")

    print("\n沪深300ETF实时行情：")
    print(df.to_string(index=False))

    # 数据包含以下字段：
    # - symbol: ETF代码
    # - price: 最新价
    # - change: 涨跌额
    # - pct_change: 涨跌幅
    # - volume: 成交量
    # - amount: 成交额


def example_etf_info():
    """示例3：获取ETF基本信息"""
    print("\n" + "=" * 60)
    print("示例3：获取ETF基本信息")
    print("=" * 60)

    # 使用 ETF 工厂获取 ETF 列表
    df = ETFFactory.call_provider_method("get_etf_spot", source="eastmoney")

    # 过滤特定ETF
    if not df.empty and "symbol" in df.columns:
        df = df[df["symbol"] == "510300"]

    print("\nETF基本信息：")
    print(df.to_string(index=False))


def example_multiple_etfs():
    """示例4：批量获取多个ETF数据"""
    print("\n" + "=" * 60)
    print("示例4：批量获取多个ETF数据")
    print("=" * 60)

    etf_list = [
        ("510300", "沪深300ETF"),
        ("510500", "中证500ETF"),
        ("159915", "创业板ETF"),
    ]

    for symbol, name in etf_list:
        print(f"\n{name} ({symbol})：")

        # 获取实时行情
        df = get_realtime_data(symbol=symbol, source="eastmoney_direct")

        if not df.empty:
            latest = df.iloc[0]
            print(f"  最新价: {latest['price']:.3f}")
            print(f"  涨跌幅: {latest['pct_change']:.2f}%")
            print(f"  成交量: {latest['volume']:.0f}手")


def example_etf_minute_data():
    """示例5：获取ETF分钟线数据"""
    print("\n" + "=" * 60)
    print("示例5：获取ETF分钟线数据")
    print("=" * 60)

    # 获取15分钟K线数据
    df = get_hist_data(
        symbol="510300",
        interval="minute",
        interval_multiplier=15,
        start_date="2024-12-01",
        end_date="2024-12-31",
        source="eastmoney_direct",
    )

    print(f"\n获取到 {len(df)} 条15分钟数据")
    print("\n最近10条数据：")
    print(df.head(10).to_string(index=False))


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one ETF数据获取示例")
    print("=" * 60)

    # 运行所有示例
    example_etf_hist_data()
    example_etf_realtime()
    example_etf_info()
    example_multiple_etfs()
    example_etf_minute_data()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
