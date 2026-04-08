#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 10：周线和月线数据分析

本示例展示如何使用 akshare-one 获取和分析周月线数据，包括：
- 获取周K线数据
- 获取月K线数据
- 对比日/周/月线数据差异
- 计算不同周期的收益率

运行方式：
    python examples/basic/10_weekly_monthly_data.py
"""

import pandas as pd
from datetime import datetime, timedelta
from akshare_one import get_hist_data


def example_weekly_data():
    """场景1：获取周K线数据"""
    print("\n" + "=" * 60)
    print("场景1：获取周K线数据")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="600519",
            interval="week",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        print(f"\n获取到 {len(df)} 条周线数据")
        print("\n数据字段：", list(df.columns))
        print("\n最近8周数据：")
        print(df.head(8).to_string(index=False))
        print("\n周线数据统计：")
        print(f"  平均周成交量: {df['volume'].mean():.0f}手")
        print(f"  最高周收盘价: {df['close'].max():.2f}")
        print(f"  最低周收盘价: {df['close'].min():.2f}")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_monthly_data():
    """场景2：获取月K线数据"""
    print("\n" + "=" * 60)
    print("场景2：获取月K线数据")
    print("=" * 60)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

    try:
        df = get_hist_data(
            symbol="600519",
            interval="month",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        print(f"\n获取到 {len(df)} 条月线数据")
        print("\n最近12个月数据：")
        print(df.head(12).to_string(index=False))

        df["pct_change"] = df["close"].pct_change() * 100

        print("\n月线数据统计：")
        print(f"  平均月成交量: {df['volume'].mean():.0f}手")
        if len(df["pct_change"].dropna()) > 0:
            print(f"  平均月涨跌幅: {df['pct_change'].mean():.2f}%")
            print(f"  最大月涨幅: {df['pct_change'].max():.2f}%")
            print(f"  最大月跌幅: {df['pct_change'].min():.2f}%")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_compare_intervals():
    """场景3：对比日/周/月线数据差异"""
    print("\n" + "=" * 60)
    print("场景3：对比日/周/月线数据差异")
    print("=" * 60)

    symbol = "600519"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    try:
        df_day = get_hist_data(
            symbol=symbol,
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        df_week = get_hist_data(
            symbol=symbol,
            interval="week",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        df_month = get_hist_data(
            symbol=symbol,
            interval="month",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )

        print(f"\n数据量对比：")
        print(f"  日线: {len(df_day)} 条")
        print(f"  周线: {len(df_week)} 条")
        print(f"  月线: {len(df_month)} 条")

        print(f"\n价格范围对比：")
        print(f"  日线 - 最高: {df_day['high'].max():.2f}, 最低: {df_day['low'].min():.2f}")
        print(f"  周线 - 最高: {df_week['high'].max():.2f}, 最低: {df_week['low'].min():.2f}")
        print(f"  月线 - 最高: {df_month['high'].max():.2f}, 最低: {df_month['low'].min():.2f}")

        print(f"\n成交量统计对比：")
        print(f"  日线 - 平均: {df_day['volume'].mean():.0f}手, 总量: {df_day['volume'].sum():.0f}手")
        print(f"  周线 - 平均: {df_week['volume'].mean():.0f}手, 总量: {df_week['volume'].sum():.0f}手")
        print(f"  月线 - 平均: {df_month['volume'].mean():.0f}手, 总量: {df_month['volume'].sum():.0f}手")

        print(f"\n最新收盘价对比：")
        print(f"  日线最新: {df_day.iloc[-1]['close']:.2f} ({df_day.iloc[-1]['timestamp']})")
        print(f"  周线最新: {df_week.iloc[-1]['close']:.2f} ({df_week.iloc[-1]['timestamp']})")
        print(f"  月线最新: {df_month.iloc[-1]['close']:.2f} ({df_month.iloc[-1]['timestamp']})")
    except Exception as e:
        print(f"\n获取数据失败: {e}")


def example_period_returns():
    """场景4：计算不同周期的收益率"""
    print("\n" + "=" * 60)
    print("场景4：计算不同周期的收益率")
    print("=" * 60)

    symbol = "600519"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

    try:
        df_day = get_hist_data(
            symbol=symbol,
            interval="day",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        df_week = get_hist_data(
            symbol=symbol,
            interval="week",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )
        df_month = get_hist_data(
            symbol=symbol,
            interval="month",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
            source="eastmoney_direct",
        )

        print(f"\n股票代码: {symbol}")
        print(f"分析周期: {start_date} ~ {end_date}")

        def calc_returns(df, name):
            df = df.copy()
            df["pct_change"] = df["close"].pct_change() * 100

            total_return = (df.iloc[-1]["close"] / df.iloc[0]["close"] - 1) * 100
            annual_return = total_return / ((df.iloc[-1]["timestamp"] - df.iloc[0]["timestamp"]).days / 365)

            positive_periods = (df["pct_change"] > 0).sum()
            negative_periods = (df["pct_change"] < 0).sum()

            return {
                "name": name,
                "count": len(df),
                "total_return": total_return,
                "annual_return": annual_return,
                "avg_change": df["pct_change"].mean(),
                "max_up": df["pct_change"].max(),
                "max_down": df["pct_change"].min(),
                "positive_count": positive_periods,
                "negative_count": negative_periods,
                "win_rate": positive_periods / (positive_periods + negative_periods) * 100
                if (positive_periods + negative_periods) > 0
                else 0,
            }

        stats_day = calc_returns(df_day, "日线")
        stats_week = calc_returns(df_week, "周线")
        stats_month = calc_returns(df_month, "月线")

        print(f"\n{'指标':<15} {'日线':<15} {'周线':<15} {'月线':<15}")
        print("-" * 60)
        print(f"{'数据条数':<15} {stats_day['count']:<15} {stats_week['count']:<15} {stats_month['count']:<15}")
        print(
            f"{'总收益率':<15} {stats_day['total_return']:.2f}%{'':<8} {stats_week['total_return']:.2f}%{'':<8} {stats_month['total_return']:.2f}%"
        )
        print(
            f"{'年化收益率':<15} {stats_day['annual_return']:.2f}%{'':<7} {stats_week['annual_return']:.2f}%{'':<7} {stats_month['annual_return']:.2f}%"
        )
        print(
            f"{'平均涨跌幅':<15} {stats_day['avg_change']:.2f}%{'':<8} {stats_week['avg_change']:.2f}%{'':<8} {stats_month['avg_change']:.2f}%"
        )
        print(
            f"{'最大涨幅':<15} {stats_day['max_up']:.2f}%{'':<9} {stats_week['max_up']:.2f}%{'':<9} {stats_month['max_up']:.2f}%"
        )
        print(
            f"{'最大跌幅':<15} {stats_day['max_down']:.2f}%{'':<9} {stats_week['max_down']:.2f}%{'':<9} {stats_month['max_down']:.2f}%"
        )
        print(
            f"{'上涨次数':<15} {stats_day['positive_count']:<15} {stats_week['positive_count']:<15} {stats_month['positive_count']:<15}"
        )
        print(
            f"{'下跌次数':<15} {stats_day['negative_count']:<15} {stats_week['negative_count']:<15} {stats_month['negative_count']:<15}"
        )
        print(
            f"{'胜率':<15} {stats_day['win_rate']:.1f}%{'':<10} {stats_week['win_rate']:.1f}%{'':<10} {stats_month['win_rate']:.1f}%"
        )
    except Exception as e:
        print(f"\n获取数据失败: {e}")

    print(f"\n波动率分析（标准差）：")
    print(f"  日线波动率: {df_day['close'].pct_change().std() * 100:.2f}%")
    print(f"  周线波动率: {df_week['close'].pct_change().std() * 100:.2f}%")
    print(f"  月线波动率: {df_month['close'].pct_change().std() * 100:.2f}%")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 周线和月线数据分析示例")
    print("=" * 60)

    example_weekly_data()
    example_monthly_data()
    example_compare_intervals()
    example_period_returns()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
