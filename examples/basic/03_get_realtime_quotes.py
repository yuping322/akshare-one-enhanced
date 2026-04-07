#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 3：获取实时行情

本示例展示如何使用 akshare-one 获取实时行情数据，包括：
- 获取单个股票实时行情
- 获取市场全量行情
- 使用多数据源获取实时数据

运行方式：
    python examples/basic/03_get_realtime_quotes.py
"""

import time
from akshare_one import get_realtime_data, get_realtime_data_multi_source


def example_single_stock():
    """示例1：获取单个股票实时行情"""
    print("\n" + "=" * 60)
    print("示例1：获取单个股票实时行情")
    print("=" * 60)

    # 获取浦发银行实时行情
    df = get_realtime_data(
        symbol="600000",
        source="eastmoney_direct"
    )

    print("\n浦发银行(600000)实时行情：")
    print(df.to_string(index=False))

    # 数据字段说明：
    # - symbol: 股票代码
    # - price: 最新价
    # - change: 涨跌额
    # - pct_change: 涨跌幅(%)
    # - open: 今开
    # - high: 最高
    # - low: 最低
    # - prev_close: 昨收
    # - volume: 成交量(手)
    # - amount: 成交额(元)
    # - timestamp: 时间戳


def example_market_overview():
    """示例2：获取市场全量行情"""
    print("\n" + "=" * 60)
    print("示例2：获取市场全量行情")
    print("=" * 60)

    # 不指定symbol，获取全市场行情
    df = get_realtime_data(source="eastmoney_direct")

    print(f"\n获取到 {len(df)} 只股票的实时行情")
    print("\n涨幅前10：")

    # 按涨跌幅排序
    df_sorted = df.sort_values('pct_change', ascending=False)
    print(df_sorted.head(10).to_string(index=False))

    print("\n跌幅前10：")
    print(df_sorted.tail(10).to_string(index=False))


def example_realtime_monitoring():
    """示例3：实时监控股票行情"""
    print("\n" + "=" * 60)
    print("示例3：实时监控股票行情（每5秒刷新一次）")
    print("=" * 60)

    stocks = ["600000", "000001", "600519"]

    print("\n开始监控，按 Ctrl+C 停止...")
    print("-" * 60)

    try:
        for i in range(3):  # 演示3次刷新
            print(f"\n第 {i+1} 次刷新：")
            for symbol in stocks:
                df = get_realtime_data(symbol=symbol, source="eastmoney_direct")
                if not df.empty:
                    latest = df.iloc[0]
                    print(
                        f"  {symbol}: "
                        f"价格={latest['price']:.2f}, "
                        f"涨跌幅={latest['pct_change']:.2f}%, "
                        f"成交量={latest['volume']:.0f}手"
                    )
            if i < 2:  # 最后一次不等待
                time.sleep(5)
    except KeyboardInterrupt:
        print("\n监控已停止")


def example_multi_source_realtime():
    """示例4：多数据源实时行情"""
    print("\n" + "=" * 60)
    print("示例4：多数据源实时行情")
    print("=" * 60)

    # 使用多数据源获取实时行情
    # 自动切换数据源，提高可靠性
    df = get_realtime_data_multi_source(
        symbol="600000",
        sources=["eastmoney_direct", "eastmoney", "xueqiu"]
    )

    print("\n使用多数据源获取的实时行情：")
    print(df.to_string(index=False))


def example_realtime_stats():
    """示例5：实时行情统计分析"""
    print("\n" + "=" * 60)
    print("示例5：实时行情统计分析")
    print("=" * 60)

    # 获取全市场行情
    df = get_realtime_data(source="eastmoney_direct")

    if not df.empty:
        print("\n市场统计：")
        print(f"  上涨股票数: {len(df[df['pct_change'] > 0])}")
        print(f"  下跌股票数: {len(df[df['pct_change'] < 0])}")
        print(f"  平盘股票数: {len(df[df['pct_change'] == 0])}")

        print("\n涨跌幅分布：")
        print(f"  涨停(≥9.9%): {len(df[df['pct_change'] >= 9.9])}")
        print(f"  涨幅5-9.9%: {len(df[(df['pct_change'] >= 5) & (df['pct_change'] < 9.9)])}")
        print(f"  涨幅0-5%: {len(df[(df['pct_change'] > 0) & (df['pct_change'] < 5)])}")
        print(f"  跌幅0-5%: {len(df[(df['pct_change'] < 0) & (df['pct_change'] > -5)])}")
        print(f"  跌幅5-9.9%: {len(df[(df['pct_change'] <= -5) & (df['pct_change'] > -9.9)])}")
        print(f"  跌停(≤-9.9%): {len(df[df['pct_change'] <= -9.9])}")

        print("\n市场强弱指标：")
        print(f"  平均涨跌幅: {df['pct_change'].mean():.2f}%")
        print(f"  涨跌幅中位数: {df['pct_change'].median():.2f}%")
        print(f"  最大涨幅: {df['pct_change'].max():.2f}%")
        print(f"  最大跌幅: {df['pct_change'].min():.2f}%")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 实时行情获取示例")
    print("=" * 60)

    # 运行所有示例
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