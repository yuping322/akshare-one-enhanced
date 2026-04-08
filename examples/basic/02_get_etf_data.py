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
from datetime import datetime, timedelta
from akshare_one import get_hist_data, get_realtime_data
from akshare_one.modules.etf import ETFFactory


def example_etf_hist_data():
    """示例1：获取ETF历史数据"""
    print("\n" + "=" * 60)
    print("示例1：获取ETF历史数据")
    print("=" * 60)

    # 使用最近30天数据，减少资源消耗
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="510300",
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print(f"\n获取到 {len(df)} 条ETF日线数据")
        print("\n最近5天的数据：")
        print(df.head().to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_etf_realtime():
    """示例2：获取ETF实时行情"""
    print("\n" + "=" * 60)
    print("示例2：获取ETF实时行情")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")

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
    print("注意：ETF实时数据源（eastmoney）当前不可用，跳过此示例")


def example_multiple_etfs():
    """示例4：批量获取多个ETF数据"""
    print("\n" + "=" * 60)
    print("示例4：批量获取多个ETF数据")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_etf_minute_data():
    """示例5：获取ETF分钟线数据"""
    print("\n" + "=" * 60)
    print("示例5：获取ETF分钟线数据")
    print("=" * 60)
    print("注意：ETF分钟线数据源当前不可用，跳过此示例")


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
    import sys
    main()
    sys.exit(0)
