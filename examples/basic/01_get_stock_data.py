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
from datetime import datetime, timedelta
from akshare_one import get_hist_data, get_hist_data_multi_source


def example_daily_data():
    """示例1：获取日线数据"""
    print("\n" + "=" * 60)
    print("示例1：获取股票日线数据")
    print("=" * 60)

    # 使用最近30天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="600000",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print(f"\n获取到 {len(df)} 条日线数据")
        print("\n最近5天的数据：")
        print(df.head().to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")

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

    # 使用最近5天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="000001",
            interval="minute",
            interval_multiplier=5,
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print(f"\n获取到 {len(df)} 条5分钟数据")
        print("\n最近10条数据：")
        print(df.head(10).to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_weekly_monthly():
    """示例3：获取周线和月线数据"""
    print("\n" + "=" * 60)
    print("示例3：获取周线和月线数据")
    print("=" * 60)

    # 使用最近90天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    try:
        df_week = get_hist_data(
            symbol="600519", interval="week", start_date=start_date, end_date=end_date, source="sina"
        )
        print(f"\n周线数据：{len(df_week)} 条")
        print(df_week.head().to_string(index=False))
    except Exception as e:
        print(f"获取周线数据失败: {e}")

    try:
        df_month = get_hist_data(
            symbol="600519", interval="month", start_date=start_date, end_date=end_date, source="sina"
        )
        print(f"\n月线数据：{len(df_month)} 条")
        print(df_month.head().to_string(index=False))
    except Exception as e:
        print(f"获取月线数据失败: {e}")


def example_adjusted_data():
    """示例4：复权数据处理"""
    print("\n" + "=" * 60)
    print("示例4：复权数据处理")
    print("=" * 60)

    # 使用最近30天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        df_none = get_hist_data(
            symbol="600000",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
    except Exception as e:
        print(f"获取不复权数据失败: {e}")
        return

    try:
        df_qfq = get_hist_data(
            symbol="600000",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="sina",
        )
    except Exception as e:
        print(f"获取前复权数据失败: {e}")
        df_qfq = pd.DataFrame()

    try:
        df_hfq = get_hist_data(
            symbol="600000",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
            source="sina",
        )
    except Exception as e:
        print(f"获取后复权数据失败: {e}")
        df_hfq = pd.DataFrame()

    print(f"\n不复权数据：{len(df_none)} 条")
    print(f"前复权数据：{len(df_qfq)} 条")
    print(f"后复权数据：{len(df_hfq)} 条")

    if len(df_none) > 0 and len(df_qfq) > 0:
        print("\n价格对比（最近一天）：")
        latest_none = df_none.iloc[-1]
        latest_qfq = df_qfq.iloc[-1] if len(df_qfq) > 0 else None
        latest_hfq = df_hfq.iloc[-1] if len(df_hfq) > 0 else None
        print(f"  不复权收盘价: {latest_none['close']:.2f}")
        if latest_qfq is not None:
            print(f"  前复权收盘价: {latest_qfq['close']:.2f}")
        if latest_hfq is not None:
            print(f"  后复权收盘价: {latest_hfq['close']:.2f}")


def example_multi_source():
    """示例5：多数据源自动切换"""
    print("\n" + "=" * 60)
    print("示例5：多数据源自动切换")
    print("=" * 60)

    # 使用最近30天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data_multi_source(
            symbol="600000",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            sources=["sina"],
        )
        print(f"\n获取到 {len(df)} 条数据")
        print("\n数据预览：")
        print(df.head().to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


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
