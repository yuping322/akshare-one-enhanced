#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 9：获取分钟线数据

本示例展示如何使用 akshare-one 获取股票分钟线数据，包括：
- 获取不同时间间隔的分钟K线数据（5分钟、15分钟、30分钟、60分钟）
- 展示数据量统计和时间范围
- 分钟线数据可视化（可选）

运行方式：
    python examples/basic/09_minute_data.py
"""

import pandas as pd
from datetime import datetime, timedelta
from akshare_one import get_hist_data

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def print_data_summary(df: pd.DataFrame, title: str):
    """打印数据统计信息

    Args:
        df: 数据DataFrame
        title: 标题
    """
    print(f"\n{title}")
    print("-" * 60)
    print(f"数据量: {len(df)} 条")

    if len(df) > 0:
        if "timestamp" in df.columns:
            print(f"时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
        print(f"\n前5条数据:")
        print(df.head().to_string(index=False))
        print(f"\n后5条数据:")
        print(df.tail().to_string(index=False))

        print(f"\n价格统计:")
        if "open" in df.columns and not df["open"].isna().all():
            print(f"  开盘价范围: {df['open'].min():.2f} - {df['open'].max():.2f}")
        if "close" in df.columns and not df["close"].isna().all():
            print(f"  收盘价范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
        if "high" in df.columns and not df["high"].isna().all():
            print(f"  最高价范围: {df['high'].min():.2f} - {df['high'].max():.2f}")
        if "low" in df.columns and not df["low"].isna().all():
            print(f"  最低价范围: {df['low'].min():.2f} - {df['low'].max():.2f}")
        print(f"\n成交量统计:")
        if "volume" in df.columns and not df["volume"].isna().all():
            print(f"  平均成交量: {df['volume'].mean():.0f} 手")
            print(f"  最大成交量: {df['volume'].max():.0f} 手")
            print(f"  最小成交量: {df['volume'].min():.0f} 手")
    else:
        print("警告: 未获取到数据")


def example_5min_data():
    """场景1：获取5分钟K线数据"""
    print("\n" + "=" * 60)
    print("场景1：获取5分钟K线数据")
    print("=" * 60)

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
        print_data_summary(df, "5分钟K线数据")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_15min_data():
    """场景2：获取15分钟K线数据"""
    print("\n" + "=" * 60)
    print("场景2：获取15分钟K线数据")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="600000",
            interval="minute",
            interval_multiplier=15,
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print_data_summary(df, "15分钟K线数据")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_30min_data():
    """场景3：获取30分钟K线数据"""
    print("\n" + "=" * 60)
    print("场景3：获取30分钟K线数据")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="600519",
            interval="minute",
            interval_multiplier=30,
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print_data_summary(df, "30分钟K线数据")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_60min_data():
    """场景4：获取60分钟K线数据"""
    print("\n" + "=" * 60)
    print("场景4：获取60分钟K线数据")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="000002",
            interval="minute",
            interval_multiplier=60,
            start_date=start_date,
            end_date=end_date,
            adjust="none",
            source="sina",
        )
        print_data_summary(df, "60分钟K线数据")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_visualization():
    """场景5：分钟线数据可视化（可选）"""
    print("\n" + "=" * 60)
    print("场景5：分钟线数据可视化")
    print("=" * 60)

    if not HAS_MATPLOTLIB:
        print("\n提示: matplotlib未安装，跳过可视化演示")
        print("如需使用可视化功能，请运行: pip install matplotlib")
        return

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
        if len(df) == 0:
            print("未获取到数据，无法可视化")
            return
    except Exception as e:
        print(f"获取数据失败: {e}")
        return

    print(f"\n准备可视化 {len(df)} 条5分钟K线数据...")

    try:
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
        fig.suptitle("5分钟K线数据 - 平安银行(000001)", fontsize=14, fontweight="bold")

        df_plot = df.copy()
        df_plot["timestamp"] = pd.to_datetime(df_plot["timestamp"])

        ax1.plot(df_plot["timestamp"], df_plot["close"], label="收盘价", color="blue", linewidth=1)
        ax1.fill_between(df_plot["timestamp"], df_plot["low"], df_plot["high"], alpha=0.2, label="价格区间")
        ax1.set_ylabel("价格（元）")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        ax2.bar(df_plot["timestamp"], df_plot["volume"], color="steelblue", alpha=0.7, label="成交量")
        ax2.set_xlabel("时间")
        ax2.set_ylabel("成交量（手）")
        ax2.legend(loc="upper left")
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        ax2.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        output_file = "minute_data_visualization.png"
        plt.savefig(output_file, dpi=100, bbox_inches="tight")
        print(f"\n可视化图表已保存: {output_file}")

        plt.show()

    except Exception as e:
        print(f"\n可视化失败: {e}")


def example_different_stocks():
    """附加示例：不同股票的分钟线数据对比"""
    print("\n" + "=" * 60)
    print("附加示例：不同股票的分钟线数据对比")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

    symbols = ["000001", "600000", "600519", "000002"]
    interval_multiplier = 5

    print(f"\n对比 {interval_multiplier} 分钟K线数据:")
    print("-" * 60)

    results = []
    for symbol in symbols:
        try:
            df = get_hist_data(
                symbol=symbol,
                interval="minute",
                interval_multiplier=interval_multiplier,
                start_date=start_date,
                end_date=end_date,
                adjust="none",
                source="sina",
            )
            if len(df) > 0:
                results.append(
                    {
                        "symbol": symbol,
                        "count": len(df),
                        "min_time": df["timestamp"].min(),
                        "max_time": df["timestamp"].max(),
                        "avg_close": df["close"].mean(),
                        "avg_volume": df["volume"].mean(),
                    }
                )
        except Exception as e:
            print(f"  {symbol}: 获取失败")

    if results:
        df_results = pd.DataFrame(results)
        print("\n各股票数据统计:")
        print(df_results.to_string(index=False))
    else:
        print("未获取到任何数据")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 分钟线数据获取示例")
    print("=" * 60)

    print("\n提示:")
    print("  - 分钟线数据通常只能获取近期数据（一般30天左右）")
    print("  - 不同数据源的分钟线数据范围可能不同")
    print("  - 建议使用 eastmoney_direct 数据源获取分钟线数据")

    example_5min_data()
    example_15min_data()
    example_30min_data()
    example_60min_data()
    example_visualization()
    example_different_stocks()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
