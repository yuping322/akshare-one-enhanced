#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股权质押数据示例程序

本示例展示如何使用 akshare-one 的股权质押模块获取和分析数据。

依赖：
- pandas

运行方式：
    python pledge_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#pledge
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.pledge import (
    get_equity_pledge,
    get_equity_pledge_ratio_rank,
)
from akshare_one.modules.pledge.factory import EquityPledgeFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_monitor_pledge_risk():
    """场景 1：监控股权质押风险"""
    print("\n" + "=" * 80)
    print("场景 1：监控股权质押风险")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行的股权质押数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 修复参数不匹配问题
        try:
            df = get_equity_pledge(symbol, start_date, end_date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            # 尝试使用更近的时间范围
            recent_start = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            print(f"重试使用时间范围: {recent_start} 至 {end_date}")
            df = get_equity_pledge(symbol, recent_start, end_date)

        # 数据处理
        if df.empty:
            print("无股权质押数据返回")
            return

        # 结果展示：显示最近10条质押记录
        print("\n最近10条股权质押记录：")
        display_df = df.head(10)[['shareholder_name', 'pledge_shares', 'pledge_ratio', 'pledgee', 'pledge_date']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_pledge_shares = df['pledge_shares'].sum()
        avg_pledge_ratio = df['pledge_ratio'].mean()
        max_pledge = df.loc[df['pledge_shares'].idxmax()]

        print("\n统计分析：")
        print(f"质押记录总数：{len(df)}")
        print(f"累计质押股份：{total_pledge_shares:,.0f} 股")
        print(f"平均质押比例：{avg_pledge_ratio:.2f}%")
        print(f"最大单笔质押：{max_pledge['shareholder_name']} - {max_pledge['pledge_shares']:,.0f} 股（{max_pledge['pledge_ratio']:.2f}%）")

        # 风险评估
        if avg_pledge_ratio > 50:
            risk_level = "高风险"
            risk_msg = "质押比例较高，需要密切关注"
        elif avg_pledge_ratio > 30:
            risk_level = "中等风险"
            risk_msg = "质押比例适中，需要持续监控"
        else:
            risk_level = "低风险"
            risk_msg = "质押比例较低，风险可控"

        print(f"\n风险评估：{risk_level} - {risk_msg}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能在此期间没有质押记录")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_pledge_ratio_ranking():
    """场景 2：质押比例排名"""
    print("\n" + "=" * 80)
    print("场景 2：质押比例排名")
    print("=" * 80)

    try:
        # 参数设置：查询最近交易日的质押比例排名
        # 使用更早的日期避免数据问题
        date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        top_n = 20

        print(f"\n查询日期：{date}")
        print(f"排名数量：前 {top_n} 名")

        # 接口调用 - 修复参数不匹配问题
        try:
            df = get_equity_pledge_ratio_rank(date, top_n)
        except Exception as e:
            print(f"接口调用失败: {e}")
            # 尝试使用更早的日期
            earlier_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
            print(f"重试使用更早的日期: {earlier_date}")
            df = get_equity_pledge_ratio_rank(earlier_date, top_n)

        # 数据处理
        if df.empty:
            print("无质押比例排名数据返回")
            return

        # 结果展示：显示所有排名
        print(f"\n质押比例排名前 {top_n} 的股票：")
        display_df = df[['rank', 'symbol', 'name', 'pledge_ratio', 'pledge_value']]
        print(display_df.to_string(index=False))

        # 统计分析
        avg_ratio = df['pledge_ratio'].mean()
        total_value = df['pledge_value'].sum()
        high_risk_count = len(df[df['pledge_ratio'] > 50])

        print("\n统计分析：")
        print(f"平均质押比例：{avg_ratio:.2f}%")
        print(f"累计质押市值：{total_value:,.2f} 元")
        print(f"高风险股票数量（质押比例>50%）：{high_risk_count} 只")

        # 风险提示
        if high_risk_count > 0:
            print("\n风险提示：")
            high_risk_stocks = df[df['pledge_ratio'] > 50]
            print(f"以下 {high_risk_count} 只股票质押比例超过50%，存在较高风险：")
            for _, row in high_risk_stocks.iterrows():
                print(f"  {row['symbol']} {row['name']}: {row['pledge_ratio']:.2f}%")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能没有数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("股权质押数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_monitor_pledge_risk()
    scenario_2_pledge_ratio_ranking()
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
        available_sources = EquityPledgeFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = EquityPledgeFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")

        # 通过 provider 获取数据
        df = sina_provider.get_equity_pledge(symbol, start_date, end_date)

        if df.empty:
            print("无股权质押数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
