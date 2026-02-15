#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北向资金数据示例程序

本示例展示如何使用 akshare-one 的北向资金模块获取和分析数据。

依赖：
- pandas

运行方式：
    python northbound_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#northbound
"""

from datetime import datetime, timedelta
import pandas as pd

# 导入模块
from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from akshare_one.modules.northbound.factory import NorthboundFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_analyze_northbound_flow_trend():
    """场景 1：分析北向资金流向趋势"""
    print("\n" + "=" * 80)
    print("场景 1：分析北向资金流向趋势")
    print("=" * 80)

    try:
        # 参数设置：查询最近30天的北向资金流向
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        market = "all"

        print(f"\n查询市场：{market}（沪深港通）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 增加网络错误处理
        try:
            df = get_northbound_flow(start_date, end_date, market)
        except Exception as e:
            print(f"接口调用失败: {e}")
            if "SSL" in str(e) or "Max retries" in str(e):
                print("检测到网络连接问题，尝试使用更短的时间范围...")
                # 使用更短的时间范围减少网络请求
                short_end = datetime.now().strftime("%Y-%m-%d")
                short_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                print(f"重试使用时间范围: {short_start} 至 {short_end}")
                df = get_northbound_flow(short_start, short_end, market)
            else:
                raise e

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近10天的数据
        print("\n最近10天北向资金流向数据：")
        display_df = df.head(10)[['date', 'market', 'net_buy']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_net_buy = df['net_buy'].sum()
        avg_net_buy = df['net_buy'].mean()
        max_inflow_day = df.loc[df['net_buy'].idxmax()]
        min_inflow_day = df.loc[df['net_buy'].idxmin()]
        inflow_days = len(df[df['net_buy'] > 0])
        outflow_days = len(df[df['net_buy'] < 0])

        print("\n统计分析：")
        print(f"北向资金净流入总额：{total_net_buy:,.2f} 亿元")
        print(f"日均北向资金净流入：{avg_net_buy:,.2f} 亿元")
        print(f"最大单日净流入：{max_inflow_day['net_buy']:,.2f} 亿元（{max_inflow_day['date']}）")
        print(f"最大单日净流出：{min_inflow_day['net_buy']:,.2f} 亿元（{min_inflow_day['date']}）")
        print(f"净流入天数：{inflow_days} 天")
        print(f"净流出天数：{outflow_days} 天")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：市场类型应为 'sh'（沪股通）、'sz'（深股通）或 'all'（全部）")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_track_northbound_holdings():
    """场景 2：追踪北向资金持股明细"""
    print("\n" + "=" * 80)
    print("场景 2：追踪北向资金持股明细")
    print("=" * 80)

    try:
        # 参数设置：查询贵州茅台的北向持股变化
        symbol = "600519"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（贵州茅台）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 增加网络错误处理
        try:
            df = get_northbound_holdings(symbol, start_date, end_date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            if "SSL" in str(e) or "Max retries" in str(e):
                print("检测到网络连接问题，尝试使用更短的时间范围...")
                short_end = datetime.now().strftime("%Y-%m-%d")
                short_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                print(f"重试使用时间范围: {short_start} 至 {short_end}")
                df = get_northbound_holdings(symbol, short_start, short_end)
            else:
                raise e

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近10天的持股数据
        print("\n最近10天北向持股明细：")
        display_df = df.head(10)[['date', 'symbol', 'holdings_shares', 'holdings_ratio', 'holdings_change']]
        print(display_df.to_string(index=False))

        # 统计分析
        if len(df) > 0:
            latest = df.iloc[0]
            earliest = df.iloc[-1]

            # 计算持股变化
            if pd.notna(latest['holdings_shares']) and pd.notna(earliest['holdings_shares']):
                total_change = latest['holdings_shares'] - earliest['holdings_shares']
                change_pct = (total_change / earliest['holdings_shares']) * 100 if earliest['holdings_shares'] != 0 else 0

                print("\n统计分析：")
                print(f"最新持股数量：{latest['holdings_shares']:,.0f} 股")
                if pd.notna(latest['holdings_ratio']):
                    print(f"最新持股比例：{latest['holdings_ratio']:.2f}%")
                else:
                    print("最新持股比例：数据不可用")
                print(f"期间持股变化：{total_change:,.0f} 股（{change_pct:+.2f}%）")
            else:
                print("\n统计分析：")
                print(f"最新持股数量：{latest['holdings_shares']:,.0f} 股")
                if pd.notna(latest['holdings_ratio']):
                    print(f"最新持股比例：{latest['holdings_ratio']:.2f}%")
                else:
                    print("最新持股比例：数据不可用")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600519'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有北向持股数据，请尝试其他股票")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_identify_popular_stocks():
    """场景 3：识别北向资金热门股票"""
    print("\n" + "=" * 80)
    print("场景 3：识别北向资金热门股票")
    print("=" * 80)

    try:
        # 参数设置：查询最近交易日的北向资金持股排名
        # 使用更早的日期避免网络问题
        date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        market = "all"
        top_n = 10

        print(f"\n查询日期：{date}")
        print(f"查询市场：{market}（沪深港通）")
        print(f"排名数量：前 {top_n} 名")

        # 接口调用 - 增加网络错误处理
        try:
            df = get_northbound_top_stocks(date, market, top_n)
        except Exception as e:
            print(f"接口调用失败: {e}")
            if "SSL" in str(e) or "Max retries" in str(e) or "NoneType" in str(e):
                print("检测到网络连接或数据解析问题...")
                # 尝试使用更早的日期
                earlier_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
                print(f"重试使用更早的日期: {earlier_date}")
                df = get_northbound_top_stocks(earlier_date, market, top_n)
            else:
                raise e

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示排名前10的股票
        print(f"\n北向资金持股排名前{top_n}的股票：")
        display_df = df[['rank', 'symbol', 'name', 'holdings_shares', 'holdings_ratio']]
        print(display_df.to_string(index=False))

        # 统计分析
        if 'holdings_shares' in df.columns and df['holdings_shares'].notna().any():
            total_holdings = df['holdings_shares'].sum()
            avg_holdings_ratio = df['holdings_ratio'].mean()
            top_stock = df.iloc[0]

            print("\n统计分析：")
            print(f"前{top_n}名持股总数：{total_holdings:,.0f} 股")
            print(f"前{top_n}名平均持股比例：{avg_holdings_ratio:.2f}%")
            print(f"持股最多的股票：{top_stock['name']}（{top_stock['symbol']}）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD，市场类型应为 'sh'、'sz' 或 'all'")
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
    print("北向资金数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_analyze_northbound_flow_trend()
    scenario_2_track_northbound_holdings()
    scenario_3_identify_popular_stocks()
    scenario_4_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_4_multi_source_example():
    """场景 4：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 4：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = NorthboundFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = NorthboundFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")

        # 通过 provider 获取数据
        df = sina_provider.get_northbound_flow(start_date, end_date, 'all')

        if df.empty:
            print("无北向资金数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
