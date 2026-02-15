#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
限售解禁数据示例程序

本示例展示如何使用 akshare-one 的限售解禁模块获取和分析数据。

依赖：
- pandas

运行方式：
    python restricted_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#restricted
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.restricted import (
    get_restricted_release,
    get_restricted_release_calendar,
)
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_track_release_calendar():
    """场景 1：追踪限售解禁日历"""
    print("\n" + "=" * 80)
    print("场景 1：追踪限售解禁日历")
    print("=" * 80)

    try:
        # 参数设置：查询未来3个月的解禁日历
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_restricted_release_calendar(start_date, end_date)

        # 数据处理
        if df.empty:
            print("未来3个月无限售解禁数据")
            return

        # 结果展示：显示所有解禁日期
        print("\n未来3个月限售解禁日历：")
        display_df = df[['date', 'release_stock_count', 'total_release_value']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_stocks = df['release_stock_count'].sum()
        total_value = df['total_release_value'].sum()
        avg_value_per_day = df['total_release_value'].mean()
        max_release_day = df.loc[df['total_release_value'].idxmax()]

        print("\n统计分析：")
        print(f"解禁日期总数：{len(df)} 天")
        print(f"涉及股票总数：{total_stocks} 只")
        print(f"累计解禁市值：{total_value:,.2f} 元")
        print(f"日均解禁市值：{avg_value_per_day:,.2f} 元")
        print(f"最大解禁日：{max_release_day['date']}（{max_release_day['total_release_value']:,.2f} 元，{max_release_day['release_stock_count']} 只股票）")

        # 风险提示
        high_value_days = df[df['total_release_value'] > avg_value_per_day * 2]
        if not high_value_days.empty:
            print("\n重点关注日期（解禁市值超过日均2倍）：")
            for _, row in high_value_days.iterrows():
                print(f"  {row['date']}: {row['total_release_value']:,.2f} 元（{row['release_stock_count']} 只股票）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有解禁数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_analyze_market_impact():
    """场景 2：分析解禁对市场的影响"""
    print("\n" + "=" * 80)
    print("场景 2：分析解禁对市场的影响")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行未来的解禁数据
        symbol = "600000"
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_restricted_release(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("该股票未来一年无限售解禁数据")
            return

        # 结果展示：显示所有解禁记录
        print("\n未来一年限售解禁明细：")
        display_df = df[['release_date', 'release_shares', 'release_value', 'release_type', 'shareholder_name']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_shares = df['release_shares'].sum()
        total_value = df['release_value'].sum()
        release_count = len(df)

        print("\n统计分析：")
        print(f"解禁批次：{release_count} 次")
        print(f"累计解禁股份：{total_shares:,.0f} 股")
        print(f"累计解禁市值：{total_value:,.2f} 元")

        # 按解禁类型统计
        type_stats = df.groupby('release_type').agg({
            'release_shares': 'sum',
            'release_value': 'sum'
        }).reset_index()

        print("\n按解禁类型统计：")
        for _, row in type_stats.iterrows():
            print(f"  {row['release_type']}: {row['release_shares']:,.0f} 股，{row['release_value']:,.2f} 元")

        # 市场影响评估
        max_release = df.loc[df['release_value'].idxmax()]
        print("\n市场影响评估：")
        print(f"最大单次解禁：{max_release['release_date']}（{max_release['release_value']:,.2f} 元）")
        print(f"解禁股东：{max_release['shareholder_name']}")
        print(f"解禁类型：{max_release['release_type']}")

        # 风险提示
        if total_value > 1e9:  # 超过10亿
            print(f"\n风险提示：累计解禁市值较大（{total_value:,.2f} 元），可能对股价产生较大压力")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能在此期间没有解禁数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("限售解禁数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_track_release_calendar()
    scenario_2_analyze_market_impact()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
