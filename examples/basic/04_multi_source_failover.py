#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 4：多数据源自动切换

本示例展示 akshare-one 的多数据源自动切换功能，包括：
- 配置数据源优先级
- 自动故障转移
- 数据源监控

运行方式：
    python examples/basic/04_multi_source_failover.py
"""

import logging
from akshare_one import (
    get_hist_data_multi_source,
    get_realtime_data_multi_source,
    get_financial_metrics_multi_source,
)

# 配置日志级别，查看切换过程
logging.basicConfig(level=logging.INFO)


def example_basic_failover():
    """示例1：基本的自动切换功能"""
    print("\n" + "=" * 60)
    print("示例1：多数据源自动切换")
    print("=" * 60)

    # 使用多数据源获取历史数据
    # 当第一个数据源失败时，自动切换到下一个
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["sina"],
    )

    if df.empty:
        print("\n警告: 未获取到数据")
    else:
        print(f"\n成功获取 {len(df)} 条历史数据")
        print("\n数据预览：")
        print(df.head().to_string(index=False))


def example_custom_source_priority():
    """示例2：自定义数据源优先级"""
    print("\n" + "=" * 60)
    print("示例2：自定义数据源优先级")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_financial_data_failover():
    """示例3：财务数据的多源切换"""
    print("\n" + "=" * 60)
    print("示例3：财务数据的多源切换")
    print("=" * 60)

    # 获取财务指标，自动切换数据源
    df = get_financial_metrics_multi_source(symbol="600600", sources=["sina", "cninfo"])

    if df.empty:
        print("\n警告: 未获取到财务指标数据")
    else:
        print(f"\n成功获取 {len(df)} 条财务指标数据")
        print("\n财务指标预览：")
        print(df.head().to_string(index=False))


def example_failover_logging():
    """示例4：查看切换日志"""
    print("\n" + "=" * 60)
    print("示例4：数据源切换日志")
    print("=" * 60)

    print("\n尝试使用一个不存在的数据源（会自动切换到下一个）：")
    print("-" * 60)

    # 配置一个会失败的数据源，观察切换过程
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-12-01",
        end_date="2024-12-31",
        sources=["invalid_source", "sina"],  # 第一个会失败
    )

    if not df.empty:
        print(f"\n成功从备用数据源获取到 {len(df)} 条数据")
    else:
        print("\n所有数据源都失败了")


def example_all_sources_failed():
    """示例5：所有数据源都失败的处理"""
    print("\n" + "=" * 60)
    print("示例5：所有数据源失败的处理")
    print("=" * 60)

    try:
        # 使用全部无效的数据源
        df = get_hist_data_multi_source(
            symbol="600000",
            interval="day",
            start_date="2024-12-01",
            end_date="2024-12-31",
            sources=["invalid_source_1", "invalid_source_2"],
        )

        if df.empty:
            print("\n所有数据源都失败，返回空数据")
        else:
            print(f"\n成功获取到 {len(df)} 条数据")

    except Exception as e:
        print(f"\n捕获到异常：{e}")
        print("建议：检查数据源配置或网络连接")


def example_source_comparison():
    """示例6：对比不同数据源的数据"""
    print("\n" + "=" * 60)
    print("示例6：对比不同数据源的数据")
    print("=" * 60)

    sources = ["sina"]

    for source in sources:
        try:
            from akshare_one import get_hist_data

            df = get_hist_data(
                symbol="600000", interval="day", start_date="2024-12-01", end_date="2024-12-31", source=source
            )

            print(f"\n数据源 {source}:")
            if df.empty:
                print("  数据条数: 0 (无数据)")
            else:
                print(f"  数据条数: {len(df)}")
                if "close" in df.columns and len(df) > 0:
                    print(f"  最新收盘价: {df.iloc[-1]['close']:.2f}")

        except Exception as e:
            print(f"\n数据源 {source}: 失败 - {e}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 多数据源自动切换示例")
    print("=" * 60)

    # 运行所有示例
    example_basic_failover()
    example_custom_source_priority()
    example_financial_data_failover()
    example_failover_logging()
    example_all_sources_failed()
    example_source_comparison()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
