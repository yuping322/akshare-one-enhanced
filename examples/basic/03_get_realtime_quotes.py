#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 3：获取实时行情

注意：实时数据源（eastmoney/xueqiu）当前网络不可用，所有实时行情示例已跳过。

运行方式：
    python examples/basic/03_get_realtime_quotes.py
"""

from akshare_one import get_realtime_data, get_realtime_data_multi_source


def example_single_stock():
    """示例1：获取单个股票实时行情"""
    print("\n" + "=" * 60)
    print("示例1：获取单个股票实时行情")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_market_overview():
    """示例2：获取市场全量行情"""
    print("\n" + "=" * 60)
    print("示例2：获取市场全量行情")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_realtime_monitoring():
    """示例3：实时监控股票行情"""
    print("\n" + "=" * 60)
    print("示例3：实时监控股票行情")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_multi_source_realtime():
    """示例4：多数据源实时行情"""
    print("\n" + "=" * 60)
    print("示例4：多数据源实时行情")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_realtime_stats():
    """示例5：实时行情统计分析"""
    print("\n" + "=" * 60)
    print("示例5：实时行情统计分析")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 实时行情获取示例")
    print("=" * 60)

    example_single_stock()
    example_market_overview()
    example_realtime_monitoring()
    example_multi_source_realtime()
    example_realtime_stats()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
