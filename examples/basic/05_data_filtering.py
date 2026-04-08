#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 5：数据过滤和处理

本示例展示如何使用 akshare-one 进行数据过滤和处理，包括：
- 基础数据过滤
- 排序和筛选
- 数据统计分析

运行方式：
    python examples/basic/05_data_filtering.py
"""

import pandas as pd
from datetime import datetime, timedelta
from akshare_one import get_hist_data_multi_source, get_realtime_data_multi_source, apply_data_filter


def example_basic_filtering():
    """示例1：基础数据过滤"""
    print("\n" + "=" * 60)
    print("示例1：基础数据过滤")
    print("=" * 60)

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

        if df.empty:
            print("\n警告: 未获取到数据")
            return

        df["pct_change"] = df["close"].pct_change() * 100
        big_moves = df[df["pct_change"].abs() > 3]

        print(f"\n原始数据: {len(df)} 条")
        print(f"涨跌幅超过3%的天数: {len(big_moves)} 条")

        if not big_moves.empty and "timestamp" in df.columns and "close" in df.columns and "pct_change" in df.columns:
            print("\n大涨天数（涨幅>3%）：")
            up_days = big_moves[big_moves["pct_change"] > 3]
            print(up_days[["timestamp", "close", "pct_change"]].head(10).to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_column_filtering():
    """示例2：列过滤（只保留需要的列）"""
    print("\n" + "=" * 60)
    print("示例2：列过滤")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_sorting_and_top_n():
    """示例3：排序和取前N条"""
    print("\n" + "=" * 60)
    print("示例3：排序和取前N条")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_query_filtering():
    """示例4：使用查询表达式过滤"""
    print("\n" + "=" * 60)
    print("示例4：使用查询表达式过滤")
    print("=" * 60)

    try:
        df = get_realtime_data_multi_source(symbol="000001", sources=["eastmoney_direct", "xueqiu"])
        if df.empty:
            print("\n警告: 未获取到数据")
            return
        df_filtered = apply_data_filter(
            df,
            columns=["symbol", "price", "pct_change", "volume"],
            row_filter={
                "query": "pct_change > 3 and pct_change < 9.9 and volume > 10000",
                "sort_by": "pct_change",
                "ascending": False,
                "top_n": 20,
            },
        )
        if not df_filtered.empty:
            print("\n涨幅3%-9.9%且成交量>1万手的股票：")
            print(df_filtered.to_string(index=False))
        else:
            print("\n没有符合条件的数据")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_sampling():
    """示例5：数据采样"""
    print("\n" + "=" * 60)
    print("示例5：数据采样")
    print("=" * 60)

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
        if df.empty:
            print("\n警告: 未获取到数据")
            return
        print(f"\n原始数据: {len(df)} 条")
        df_sample = apply_data_filter(df, row_filter={"sample": 0.2})
        print(f"采样后数据: {len(df_sample)} 条")
        if not df_sample.empty:
            print("\n采样数据预览：")
            print(df_sample.head().to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_combined_filtering():
    """示例6：组合过滤"""
    print("\n" + "=" * 60)
    print("示例6：组合过滤")
    print("=" * 60)

    try:
        df = get_realtime_data_multi_source(symbol="000001", sources=["eastmoney_direct", "xueqiu"])
        if df.empty:
            print("\n警告: 未获取到数据")
            return
        df_filtered = apply_data_filter(
            df,
            columns=["symbol", "price", "pct_change", "volume", "amount"],
            row_filter={
                "query": "pct_change > 2 and volume > 50000",
                "sort_by": "pct_change",
                "ascending": False,
                "top_n": 20,
            },
        )
        print(f"\n原始数据: {len(df)} 条")
        print(f"过滤后数据: {len(df_filtered)} 条")
        if not df_filtered.empty:
            print("\n过滤结果：")
            print(df_filtered.to_string(index=False))
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_statistical_analysis():
    """示例7：统计分析"""
    print("\n" + "=" * 60)
    print("示例7：数据统计分析")
    print("=" * 60)

    # 获取历史数据
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["sina"],
    )

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    # 计算涨跌幅
    df["pct_change"] = df["close"].pct_change() * 100

    # 统计分析
    print("\n价格统计：")
    if "close" in df.columns and not df["close"].isna().all():
        print(f"  平均收盘价: {df['close'].mean():.2f}")
    if "high" in df.columns and not df["high"].isna().all():
        print(f"  最高价: {df['high'].max():.2f}")
    if "low" in df.columns and not df["low"].isna().all():
        print(f"  最低价: {df['low'].min():.2f}")
    if "close" in df.columns and not df["close"].isna().all():
        print(f"  价格标准差: {df['close'].std():.2f}")

    print("\n涨跌幅统计：")
    if "pct_change" in df.columns and not df["pct_change"].isna().all():
        mean_pct = df["pct_change"].mean()
        if pd.notna(mean_pct):
            print(f"  平均涨跌幅: {mean_pct:.2f}%")
        max_pct = df["pct_change"].max()
        if pd.notna(max_pct):
            print(f"  最大涨幅: {max_pct:.2f}%")
        min_pct = df["pct_change"].min()
        if pd.notna(min_pct):
            print(f"  最大跌幅: {min_pct:.2f}%")
        std_pct = df["pct_change"].std()
        if pd.notna(std_pct):
            print(f"  涨跌幅标准差: {std_pct:.2f}%")

    print("\n成交量统计：")
    if "volume" in df.columns and not df["volume"].isna().all():
        print(f"  平均成交量: {df['volume'].mean():.0f}手")
        print(f"  最大成交量: {df['volume'].max():.0f}手")
        print(f"  最小成交量: {df['volume'].min():.0f}手")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 数据过滤和处理示例")
    print("=" * 60)

    # 运行所有示例
    example_basic_filtering()
    example_column_filtering()
    example_sorting_and_top_n()
    example_query_filtering()
    example_sampling()
    example_combined_filtering()
    example_statistical_analysis()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
