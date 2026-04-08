#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货示例：获取期货数据

本示例展示如何使用 akshare-one 获取期货数据，包括：
- 获取期货历史数据
- 获取期货主力合约
- 获取期货实时行情

运行方式：
    python examples/futures_example.py
"""

import pandas as pd
from akshare_one import (
    get_futures_hist_data,
    get_futures_main_contracts,
    get_futures_realtime_data,
)


def example_futures_hist_data():
    """示例1：获取期货历史数据"""
    print("\n" + "=" * 60)
    print("示例1：获取期货历史数据")
    print("=" * 60)

    df = get_futures_hist_data(
        symbol="AG", contract="main", interval="day", start_date="2024-01-01", end_date="2024-12-31", source="sina"
    )

    print(f"\n获取到 {len(df)} 条历史数据")
    if not df.empty:
        print("\n最近5天的数据：")
        print(df.tail().to_string(index=False))


def example_futures_main_contracts():
    """示例2：获取期货主力合约列表"""
    print("\n" + "=" * 60)
    print("示例2：获取期货主力合约列表")
    print("=" * 60)

    df = get_futures_main_contracts(source="sina")

    print(f"\n获取到 {len(df)} 个主力合约")
    if not df.empty:
        print("\n主力合约列表：")
        print(df.to_string(index=False))


def example_futures_realtime():
    """示例3：获取期货实时行情"""
    print("\n" + "=" * 60)
    print("示例3：获取期货实时行情")
    print("=" * 60)

    df = get_futures_realtime_data(symbol="AG", source="sina")

    print(f"\n获取到 {len(df)} 条实时数据")
    if not df.empty:
        print("\n白银(AG)实时行情：")
        print(df.to_string(index=False))


def example_futures_minute_data():
    """示例4：获取期货分钟数据"""
    print("\n" + "=" * 60)
    print("示例4：获取期货分钟数据")
    print("=" * 60)

    df = get_futures_hist_data(
        symbol="CU",
        contract="main",
        interval="minute",
        interval_multiplier=5,
        start_date="2024-12-01",
        end_date="2024-12-31",
        source="sina",
    )

    print(f"\n获取到 {len(df)} 条5分钟数据")
    if not df.empty:
        print("\n最近10条数据：")
        print(df.tail(10).to_string(index=False))


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 期货数据获取示例")
    print("=" * 60)

    example_futures_hist_data()
    example_futures_main_contracts()
    example_futures_realtime()
    example_futures_minute_data()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
