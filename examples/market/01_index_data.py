#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场指数数据示例 1：获取指数数据

本示例展示如何使用 akshare-one 获取市场指数数据，包括：
- 获取上证指数历史数据
- 获取深证成指数据
- 获取创业板指数数据
- 获取沪深300指数数据
- 指数走势对比分析

运行方式：
    python examples/market/01_index_data.py
"""

import pandas as pd
from akshare_one import get_index_hist_data, get_index_realtime_data, get_index_list


def example_shanghai_index():
    """场景1：获取上证指数历史数据"""
    print("\n" + "=" * 60)
    print("场景1：获取上证指数历史数据")
    print("=" * 60)

    try:
        df = get_index_hist_data(
            symbol="000001", start_date="2024-01-01", end_date="2024-12-31", interval="daily", source="eastmoney"
        )

        if df.empty:
            print("无上证指数数据返回")
            return

        print(f"\n获取到 {len(df)} 条上证指数日线数据")
        print("\n最近5个交易日的数据：")
        print(df.head().to_string(index=False))

        latest = df.iloc[-1]
        print(f"\n最新数据：")
        print(f"  日期: {latest['timestamp']}")
        print(f"  收盘: {latest['close']:.2f}")
        print(f"  最高: {latest['high']:.2f}")
        print(f"  最低: {latest['low']:.2f}")
        print(f"  成交量: {latest['volume']:,.0f}")
    except ConnectionError as e:
        print(f"网络连接错误：{e}")
        print("提示：请检查网络连接或稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def example_shenzhen_index():
    """场景2：获取深证成指数据"""
    print("\n" + "=" * 60)
    print("场景2：获取深证成指数据")
    print("=" * 60)

    try:
        df = get_index_hist_data(
            symbol="399001", start_date="2024-01-01", end_date="2024-12-31", interval="daily", source="eastmoney"
        )

        if df.empty:
            print("无深证成指数据返回")
            return

        print(f"\n获取到 {len(df)} 条深证成指日线数据")
        print("\n最近5个交易日的数据：")
        print(df.head().to_string(index=False))

        if not df.empty:
            df["change_pct"] = df["close"].pct_change() * 100
            latest = df.iloc[-1]
            print(f"\n最新数据：")
            print(f"  日期: {latest['timestamp']}")
            print(f"  收盘: {latest['close']:.2f}")
            print(f"  涨跌幅: {latest['change_pct']:.2f}%")
    except ConnectionError as e:
        print(f"网络连接错误：{e}")
        print("提示：请检查网络连接或稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def example_chinext_index():
    """场景3：获取创业板指数数据"""
    print("\n" + "=" * 60)
    print("场景3：获取创业板指数数据")
    print("=" * 60)

    try:
        df = get_index_hist_data(
            symbol="399006", start_date="2024-01-01", end_date="2024-12-31", interval="daily", source="eastmoney"
        )

        if df.empty:
            print("无创业板指数据返回")
            return

        print(f"\n获取到 {len(df)} 条创业板指日线数据")
        print("\n最近5个交易日的数据：")
        print(df.head().to_string(index=False))

        if not df.empty:
            print(f"\n统计信息：")
            print(f"  最高价: {df['high'].max():.2f}")
            print(f"  最低价: {df['low'].min():.2f}")
            print(f"  平均价: {df['close'].mean():.2f}")
            print(f"  最大涨幅: {df['close'].pct_change().max() * 100:.2f}%")
            print(f"  最大跌幅: {df['close'].pct_change().min() * 100:.2f}%")
    except ConnectionError as e:
        print(f"网络连接错误：{e}")
        print("提示：请检查网络连接或稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def example_csi300_index():
    """场景4：获取沪深300指数数据"""
    print("\n" + "=" * 60)
    print("场景4：获取沪深300指数数据")
    print("=" * 60)

    try:
        df = get_index_hist_data(
            symbol="000300", start_date="2024-01-01", end_date="2024-12-31", interval="daily", source="eastmoney"
        )

        if df.empty:
            print("无沪深300指数数据返回")
            return

        print(f"\n获取到 {len(df)} 条沪深300指数日线数据")
        print("\n最近5个交易日的数据：")
        print(df.head().to_string(index=False))

        if not df.empty:
            print("\n获取沪深300实时行情：")
            try:
                realtime_df = get_index_realtime_data(symbol="000300", source="eastmoney")
                if not realtime_df.empty:
                    print(realtime_df.to_string(index=False))
            except Exception as e:
                print(f"获取实时行情失败: {e}")
    except ConnectionError as e:
        print(f"网络连接错误：{e}")
        print("提示：请检查网络连接或稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def example_index_comparison():
    """场景5：指数走势对比分析"""
    print("\n" + "=" * 60)
    print("场景5：指数走势对比分析")
    print("=" * 60)

    indices = {"上证指数": "000001", "深证成指": "399001", "创业板指": "399006", "沪深300": "000300"}

    print("\n正在获取各指数数据...")
    data = {}
    for name, symbol in indices.items():
        try:
            df = get_index_hist_data(
                symbol=symbol, start_date="2024-01-01", end_date="2024-12-31", interval="daily", source="eastmoney"
            )
            if not df.empty:
                data[name] = df
                print(f"  {name}: {len(df)} 条数据")
        except Exception as e:
            print(f"  {name}: 获取失败 ({e})")

    if data:
        print("\n各指数最新数据对比：")
        print("-" * 60)
        for name, df in data.items():
            if not df.empty:
                latest = df.iloc[-1]
                start = df.iloc[0]
                change_pct = (latest["close"] - start["close"]) / start["close"] * 100
                print(f"{name}:")
                print(f"  期初价格: {start['close']:.2f}")
                print(f"  最新价格: {latest['close']:.2f}")
                print(f"  期间涨跌幅: {change_pct:.2f}%")
                print()

        performance = {}
        for name, df in data.items():
            if not df.empty:
                start = df.iloc[0]
                end = df.iloc[-1]
                performance[name] = (end["close"] - start["close"]) / start["close"] * 100

        if performance:
            best = max(performance.items(), key=lambda x: x[1])
            worst = min(performance.items(), key=lambda x: x[1])
            print("-" * 60)
            print(f"表现最强指数: {best[0]} ({best[1]:.2f}%)")
            print(f"表现最弱指数: {worst[0]} ({worst[1]:.2f}%)")


def example_index_list():
    """额外场景：获取指数列表"""
    print("\n" + "=" * 60)
    print("额外场景：获取指数列表")
    print("=" * 60)

    try:
        df = get_index_list(category="cn", source="eastmoney")

        if df.empty:
            print("无指数数据返回")
            return

        print(f"\n获取到 {len(df)} 个指数")
        print("\n前10个指数：")
        print(df.head(10).to_string(index=False))
    except ConnectionError as e:
        print(f"网络连接错误：{e}")
        print("提示：请检查网络连接或稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")

    # 数据包含以下字段：
    # - symbol: 指数代码
    # - name: 指数名称
    # - type: 指数类型


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 市场指数数据获取示例")
    print("=" * 60)

    # 运行所有示例
    example_shanghai_index()
    example_shenzhen_index()
    example_chinext_index()
    example_csi300_index()
    example_index_comparison()
    example_index_list()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
