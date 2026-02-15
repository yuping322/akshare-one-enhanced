#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
融资融券数据示例程序

本示例展示如何使用 akshare-one 的融资融券模块获取和分析数据。

依赖：
- pandas

运行方式：
    python margin_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#margin
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.margin import (
    get_margin_data,
    get_margin_summary,
)
from akshare_one.modules.margin.factory import MarginFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_track_margin_balance_trend():
    """场景 1：追踪融资融券余额趋势"""
    print("\n" + "=" * 80)
    print("场景 1：追踪融资融券余额趋势")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行最近30天的融资融券数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 修复参数不匹配问题
        # 根据源码分析，接口参数应该是正确的，增加错误处理
        try:
            df = get_margin_data(symbol, start_date, end_date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            # 尝试使用更近的日期范围，因为融资融券数据更新频率较高
            recent_start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
            print(f"重试使用更近的日期范围: {recent_start} 至 {end_date}")
            df = get_margin_data(symbol, recent_start, end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近10天的数据
        print("\n最近10天融资融券数据：")
        display_df = df.head(10)[['date', 'margin_balance', 'margin_buy', 'short_balance', 'total_balance']]
        print(display_df.to_string(index=False))

        # 统计分析
        latest_data = df.iloc[0]
        avg_margin_balance = df['margin_balance'].mean()
        max_margin_balance = df['margin_balance'].max()
        max_margin_day = df.loc[df['margin_balance'].idxmax()]

        print("\n统计分析：")
        print(f"最新融资余额：{latest_data['margin_balance']:,.2f} 元")
        print(f"最新融券余额：{latest_data['short_balance']:,.2f} 元")
        print(f"最新融资融券余额：{latest_data['total_balance']:,.2f} 元")
        print(f"平均融资余额：{avg_margin_balance:,.2f} 元")
        print(f"最高融资余额：{max_margin_balance:,.2f} 元（{max_margin_day['date']}）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_identify_high_leverage_stocks():
    """场景 2：识别高杠杆股票"""
    print("\n" + "=" * 80)
    print("场景 2：识别高杠杆股票")
    print("=" * 80)

    try:
        # 参数设置：查询最近30天的融资融券汇总数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        market = "all"

        print(f"\n查询市场：{market}（全市场）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 修复参数不匹配问题
        try:
            df = get_margin_summary(start_date, end_date, market)
        except Exception as e:
            print(f"接口调用失败: {e}")
            # 尝试使用更近的日期范围
            recent_start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
            print(f"重试使用更近的日期范围: {recent_start} 至 {end_date}")
            df = get_margin_summary(recent_start, end_date, market)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 筛选全市场数据
        all_market_df = df[df['market'] == 'all'].copy()

        if all_market_df.empty:
            print("无全市场汇总数据")
            return

        # 结果展示：显示最近10天的汇总数据
        print("\n最近10天融资融券汇总数据：")
        display_df = all_market_df.head(10)[['date', 'market', 'margin_balance', 'short_balance', 'total_balance']]
        print(display_df.to_string(index=False))

        # 统计分析
        latest_data = all_market_df.iloc[0]
        avg_total_balance = all_market_df['total_balance'].mean()
        max_total_balance = all_market_df['total_balance'].max()
        min_total_balance = all_market_df['total_balance'].min()

        # 计算融资融券余额变化
        if len(all_market_df) > 1:
            balance_change = latest_data['total_balance'] - all_market_df.iloc[-1]['total_balance']
            balance_change_pct = (balance_change / all_market_df.iloc[-1]['total_balance']) * 100
        else:
            balance_change = 0
            balance_change_pct = 0

        print("\n统计分析：")
        print(f"最新融资余额：{latest_data['margin_balance']:,.2f} 元")
        print(f"最新融券余额：{latest_data['short_balance']:,.2f} 元")
        print(f"最新融资融券余额：{latest_data['total_balance']:,.2f} 元")
        print(f"平均融资融券余额：{avg_total_balance:,.2f} 元")
        print(f"最高融资融券余额：{max_total_balance:,.2f} 元")
        print(f"最低融资融券余额：{min_total_balance:,.2f} 元")
        print(f"期间余额变化：{balance_change:,.2f} 元（{balance_change_pct:+.2f}%）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：市场参数应为 'sh'、'sz' 或 'all'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("融资融券数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_track_margin_balance_trend()
    scenario_2_identify_high_leverage_stocks()
    scenario_3_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_3_multi_source_example():
    """场景 3：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 3：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = MarginFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = MarginFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")

        # 通过 provider 获取数据
        df = sina_provider.get_margin_data(symbol, start_date, end_date)

        if df.empty:
            print("无融资融券数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
