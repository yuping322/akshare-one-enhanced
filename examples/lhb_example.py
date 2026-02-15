#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙虎榜数据示例程序

本示例展示如何使用 akshare-one 的龙虎榜模块获取和分析数据。

依赖：
- pandas

运行方式：
    python lhb_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#lhb
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.lhb import (
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
    get_dragon_tiger_broker_stats,
)
from akshare_one.modules.lhb.factory import DragonTigerFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_track_hot_money():
    """场景 1：追踪龙虎榜热钱"""
    print("\n" + "=" * 80)
    print("场景 1：追踪龙虎榜热钱")
    print("=" * 80)

    try:
        # 参数设置：查询最近交易日的龙虎榜数据
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        symbol = None  # None 表示查询所有股票

        print(f"\n查询日期：{date}")
        print("查询范围：所有上榜股票")

        # 接口调用
        df = get_dragon_tiger_list(date, symbol)

        # 数据处理
        if df.empty:
            print("无龙虎榜数据返回")
            print("提示：该日期可能不是交易日或数据尚未更新，请尝试其他日期")
            return

        # 按净买入金额排序
        df_sorted = df.sort_values('net_amount', ascending=False)

        # 结果展示：显示净买入最多的前10只股票
        print("\n龙虎榜净买入最多的前10只股票：")
        display_df = df_sorted.head(10)[['symbol', 'name', 'close_price', 'pct_change', 'reason', 'net_amount', 'turnover_rate']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_buy = df['buy_amount'].sum()
        total_sell = df['sell_amount'].sum()
        total_net = df['net_amount'].sum()
        stock_count = len(df)

        # 按上榜原因统计
        reason_counts = df['reason'].value_counts()

        print("\n统计分析：")
        print(f"上榜股票总数：{stock_count}")
        print(f"龙虎榜总买入金额：{total_buy:,.2f} 万元")
        print(f"龙虎榜总卖出金额：{total_sell:,.2f} 万元")
        print(f"龙虎榜净买入金额：{total_net:,.2f} 万元")

        print("\n按上榜原因统计：")
        for reason, count in reason_counts.head(5).items():
            print(f"{reason}: {count} 只")

        # 分析热钱流向
        net_buy_stocks = len(df[df['net_amount'] > 0])
        net_sell_stocks = len(df[df['net_amount'] < 0])

        print("\n热钱流向分析：")
        print(f"净买入股票数：{net_buy_stocks}（{net_buy_stocks/stock_count*100:.1f}%）")
        print(f"净卖出股票数：{net_sell_stocks}（{net_sell_stocks/stock_count*100:.1f}%）")

        if total_net > 0:
            print("整体趋势：热钱净流入，市场情绪偏多")
        else:
            print("整体趋势：热钱净流出，市场情绪偏空")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能没有龙虎榜数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_analyze_summary():
    """场景 2：分析龙虎榜统计"""
    print("\n" + "=" * 80)
    print("场景 2：分析龙虎榜统计")
    print("=" * 80)

    try:
        # 参数设置：查询最近30天的龙虎榜汇总数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        group_by = "stock"  # 按股票分组统计

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print("分组方式：按股票统计")

        # 接口调用
        df = get_dragon_tiger_summary(start_date, end_date, group_by)

        # 数据处理
        if df.empty:
            print("无龙虎榜汇总数据返回")
            print("提示：该时间段可能没有龙虎榜数据，请尝试其他日期")
            return

        # 按上榜次数排序
        df_sorted = df.sort_values('list_count', ascending=False)

        # 结果展示：显示上榜次数最多的前10只股票
        print("\n上榜次数最多的前10只股票：")
        display_columns = ['symbol', 'name', 'list_count', 'buy_amount', 'sell_amount', 'net_amount']
        if all(col in df_sorted.columns for col in display_columns):
            print(df_sorted.head(10)[display_columns].to_string(index=False))
        else:
            print(df_sorted.head(10).to_string(index=False))

        # 统计分析
        total_stocks = len(df)
        total_list_count = df['list_count'].sum() if 'list_count' in df.columns else 0

        print("\n统计分析：")
        print(f"上榜股票总数：{total_stocks}")
        print(f"上榜总次数：{total_list_count}")

        if 'list_count' in df.columns:
            avg_list_count = df['list_count'].mean()
            max_list_count = df['list_count'].max()
            print(f"平均上榜次数：{avg_list_count:.2f}")
            print(f"最多上榜次数：{max_list_count}")

        # 资金流向分析
        if 'net_amount' in df.columns:
            net_buy_stocks = len(df[df['net_amount'] > 0])
            net_sell_stocks = len(df[df['net_amount'] < 0])
            total_net = df['net_amount'].sum()

            print("\n资金流向分析：")
            print(f"净买入股票数：{net_buy_stocks}（{net_buy_stocks/total_stocks*100:.1f}%）")
            print(f"净卖出股票数：{net_sell_stocks}（{net_sell_stocks/total_stocks*100:.1f}%）")
            print(f"期间净买入总额：{total_net:,.2f} 万元")

            if total_net > 0:
                print("整体趋势：热钱持续流入，市场活跃度较高")
            else:
                print("整体趋势：热钱持续流出，市场活跃度下降")

        # 按原因分组统计（如果支持）
        print("\n尝试按上榜原因分组统计...")
        try:
            df_reason = get_dragon_tiger_summary(start_date, end_date, group_by="reason")
            if not df_reason.empty:
                print("\n按上榜原因统计：")
                reason_columns = ['reason', 'list_count']
                if all(col in df_reason.columns for col in reason_columns):
                    df_reason_sorted = df_reason.sort_values('list_count', ascending=False)
                    print(df_reason_sorted.head(5)[reason_columns].to_string(index=False))
                else:
                    print(df_reason.head(5).to_string(index=False))
        except Exception as e:
            print(f"按原因分组统计失败：{e}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD，group_by 应为 'stock', 'broker' 或 'reason'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有龙虎榜数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_broker_activity():
    """场景 3：营业部活跃度分析"""
    print("\n" + "=" * 80)
    print("场景 3：营业部活跃度分析")
    print("=" * 80)

    try:
        # 参数设置：查询最近30天的营业部统计数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        top_n = 20  # 获取前20名最活跃的营业部

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print(f"排名数量：前 {top_n} 名")

        # 接口调用
        df = get_dragon_tiger_broker_stats(start_date, end_date, top_n)

        # 数据处理
        if df.empty:
            print("无营业部统计数据返回")
            print("提示：该时间段可能没有龙虎榜数据，请尝试其他日期")
            return

        # 结果展示：显示最活跃的营业部
        print("\n最活跃的前10家营业部：")
        display_columns = ['rank', 'broker_name', 'list_count', 'buy_amount', 'sell_amount', 'net_amount']
        if all(col in df.columns for col in display_columns):
            print(df.head(10)[display_columns].to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

        # 统计分析
        total_brokers = len(df)

        if 'list_count' in df.columns:
            total_list_count = df['list_count'].sum()
            avg_list_count = df['list_count'].mean()
            max_list_count = df['list_count'].max()

            print("\n统计分析：")
            print(f"活跃营业部总数：{total_brokers}")
            print(f"上榜总次数：{total_list_count}")
            print(f"平均上榜次数：{avg_list_count:.2f}")
            print(f"最多上榜次数：{max_list_count}")

        # 资金流向分析
        if 'buy_amount' in df.columns and 'sell_amount' in df.columns and 'net_amount' in df.columns:
            total_buy = df['buy_amount'].sum()
            total_sell = df['sell_amount'].sum()
            total_net = df['net_amount'].sum()

            # 统计净买入和净卖出的营业部数量
            net_buy_brokers = len(df[df['net_amount'] > 0])
            net_sell_brokers = len(df[df['net_amount'] < 0])

            print("\n资金流向分析：")
            print(f"总买入金额：{total_buy:,.2f} 万元")
            print(f"总卖出金额：{total_sell:,.2f} 万元")
            print(f"净买入金额：{total_net:,.2f} 万元")
            print(f"净买入营业部数：{net_buy_brokers}（{net_buy_brokers/total_brokers*100:.1f}%）")
            print(f"净卖出营业部数：{net_sell_brokers}（{net_sell_brokers/total_brokers*100:.1f}%）")

            # 分析营业部操作风格
            if total_net > 0:
                print("\n整体趋势：活跃营业部以买入为主，市场情绪偏多")
            else:
                print("\n整体趋势：活跃营业部以卖出为主，市场情绪偏空")

            # 找出最激进的买方和卖方营业部
            if 'net_amount' in df.columns and 'broker_name' in df.columns:
                top_buyer = df.loc[df['net_amount'].idxmax()]
                top_seller = df.loc[df['net_amount'].idxmin()]

                print("\n最激进的买方营业部：")
                print(f"  {top_buyer['broker_name']}")
                print(f"  净买入金额：{top_buyer['net_amount']:,.2f} 万元")

                print("\n最激进的卖方营业部：")
                print(f"  {top_seller['broker_name']}")
                print(f"  净卖出金额：{abs(top_seller['net_amount']):,.2f} 万元")

        # 交易频率分析
        if 'buy_count' in df.columns and 'sell_count' in df.columns:
            total_buy_count = df['buy_count'].sum()
            total_sell_count = df['sell_count'].sum()

            print("\n交易频率分析：")
            print(f"总买入次数：{total_buy_count}")
            print(f"总卖出次数：{total_sell_count}")

            if 'buy_amount' in df.columns and total_buy_count > 0:
                avg_buy_amount = total_buy / total_buy_count
                print(f"平均单笔买入金额：{avg_buy_amount:,.2f} 万元")

            if 'sell_amount' in df.columns and total_sell_count > 0:
                avg_sell_amount = total_sell / total_sell_count
                print(f"平均单笔卖出金额：{avg_sell_amount:,.2f} 万元")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD，top_n 应为正整数")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有龙虎榜数据，请尝试其他日期")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("龙虎榜数据示例程序")
    print("=" * 80)

    # 运行场景 1
    scenario_1_track_hot_money()

    # 运行场景 2
    scenario_2_analyze_summary()

    # 运行场景 3
    scenario_3_broker_activity()

    # 运行场景 4
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
        available_sources = DragonTigerFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = DragonTigerFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n查询日期：{date}")

        # 通过 provider 获取数据
        df = sina_provider.get_dragon_tiger_list(date, None)

        if df.empty:
            print("无龙虎榜数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
