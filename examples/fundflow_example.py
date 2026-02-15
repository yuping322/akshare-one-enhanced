#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金流数据示例程序

本示例展示如何使用 akshare-one 的资金流模块获取和分析数据。

依赖：
- pandas

运行方式：
    python fundflow_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#fundflow
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.fundflow import (
    get_stock_fund_flow,
    get_sector_fund_flow,
    get_main_fund_flow_rank,
    get_industry_list,
    get_industry_constituents,
    get_concept_list,
    get_concept_constituents,
)
from akshare_one.modules.fundflow.factory import FundFlowFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_track_stock_fund_flow():
    """场景 1：追踪个股资金流向"""
    print("\n" + "=" * 80)
    print("场景 1：追踪个股资金流向")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行最近30天的资金流向
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_stock_fund_flow(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近10天的数据
        print("\n最近10天资金流向数据：")
        display_df = df.head(10)[['date', 'close', 'pct_change', 'main_net_inflow', 'main_net_inflow_rate']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_inflow = df['main_net_inflow'].sum()
        avg_inflow = df['main_net_inflow'].mean()
        max_inflow_day = df.loc[df['main_net_inflow'].idxmax()]

        print("\n统计分析：")
        print(f"主力资金净流入总额：{total_inflow:,.2f} 万元")
        print(f"日均主力资金净流入：{avg_inflow:,.2f} 万元")
        print(f"最大单日净流入：{max_inflow_day['main_net_inflow']:,.2f} 万元（{max_inflow_day['date']}）")

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


def scenario_2_analyze_sector_rotation():
    """场景 2：分析板块资金轮动"""
    print("\n" + "=" * 80)
    print("场景 2：分析板块资金轮动")
    print("=" * 80)

    try:
        # 参数设置：查询行业板块资金流向
        sector_type = "industry"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        print(f"\n查询板块类型：{sector_type}（行业板块）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_sector_fund_flow(sector_type, start_date, end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 按主力净流入排序
        df_sorted = df.sort_values('main_net_inflow', ascending=False)

        # 结果展示：显示资金流入最多的前10个板块
        print("\n资金流入最多的前10个行业板块：")
        display_df = df_sorted.head(10)[['sector_name', 'main_net_inflow', 'pct_change', 'leading_stock']]
        print(display_df.to_string(index=False))

        # 统计分析
        top_sector = df_sorted.iloc[0]
        inflow_sectors = len(df[df['main_net_inflow'] > 0])
        outflow_sectors = len(df[df['main_net_inflow'] < 0])

        print("\n统计分析：")
        print(f"资金流入最多的板块：{top_sector['sector_name']}（{top_sector['main_net_inflow']:,.2f} 万元）")
        print(f"资金流入板块数量：{inflow_sectors}")
        print(f"资金流出板块数量：{outflow_sectors}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：板块类型应为 'industry' 或 'concept'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请稍后重试")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_main_fund_ranking():
    """场景 3：主力资金排名分析"""
    print("\n" + "=" * 80)
    print("场景 3：主力资金排名分析")
    print("=" * 80)

    try:
        # 参数设置：查询最近交易日的主力资金排名
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        indicator = "net_inflow"

        print(f"\n查询日期：{date}")
        print(f"排名指标：{indicator}（主力净流入）")

        # 接口调用
        df = get_main_fund_flow_rank(date, indicator)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示排名前10的股票
        print("\n主力资金净流入排名前10的股票：")
        display_df = df.head(10)[['rank', 'symbol', 'name', 'main_net_inflow', 'pct_change']]
        print(display_df.to_string(index=False))

        # 统计分析
        top_10_inflow = df.head(10)['main_net_inflow'].sum()
        avg_pct_change = df.head(10)['pct_change'].mean()

        print("\n统计分析：")
        print(f"前10名主力资金净流入总额：{top_10_inflow:,.2f} 万元")
        print(f"前10名平均涨跌幅：{avg_pct_change:.2f}%")

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


def scenario_4_industry_sectors():
    """场景 4：获取行业板块列表和成分股"""
    print("\n" + "=" * 80)
    print("场景 4：获取行业板块列表和成分股")
    print("=" * 80)

    try:
        # 接口调用：获取行业板块列表
        print("\n获取行业板块列表...")
        industry_df = get_industry_list()

        if industry_df.empty:
            print("无行业板块数据")
            return

        # 结果展示：显示前10个行业板块
        print("\n行业板块列表（前10个）：")
        display_df = industry_df.head(10)[['sector_code', 'sector_name', 'constituent_count']]
        print(display_df.to_string(index=False))

        # 选择第一个行业板块，获取其成分股
        first_industry = industry_df.iloc[0]
        industry_code = first_industry['sector_code']
        industry_name = first_industry['sector_name']

        print(f"\n获取 {industry_name}（{industry_code}）的成分股...")
        constituents_df = get_industry_constituents(industry_code)

        if constituents_df.empty:
            print("无成分股数据")
            return

        # 结果展示：显示前10只成分股
        print(f"\n{industry_name} 成分股（前10只）：")
        display_df = constituents_df.head(10)[['symbol', 'name']]
        print(display_df.to_string(index=False))

        # 统计分析
        print("\n统计分析：")
        print(f"行业板块总数：{len(industry_df)}")
        print(f"{industry_name} 成分股数量：{len(constituents_df)}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：数据可能暂时不可用，请稍后重试")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_5_concept_sectors():
    """场景 5：获取概念板块列表和成分股"""
    print("\n" + "=" * 80)
    print("场景 5：获取概念板块列表和成分股")
    print("=" * 80)

    try:
        # 接口调用：获取概念板块列表
        print("\n获取概念板块列表...")
        concept_df = get_concept_list()

        if concept_df.empty:
            print("无概念板块数据")
            return

        # 结果展示：显示前10个概念板块
        print("\n概念板块列表（前10个）：")
        display_df = concept_df.head(10)[['sector_code', 'sector_name', 'constituent_count']]
        print(display_df.to_string(index=False))

        # 选择第一个概念板块，获取其成分股
        first_concept = concept_df.iloc[0]
        concept_code = first_concept['sector_code']
        concept_name = first_concept['sector_name']

        print(f"\n获取 {concept_name}（{concept_code}）的成分股...")
        constituents_df = get_concept_constituents(concept_code)

        if constituents_df.empty:
            print("无成分股数据")
            return

        # 结果展示：显示前10只成分股
        print(f"\n{concept_name} 成分股（前10只）：")
        display_df = constituents_df.head(10)[['symbol', 'name']]
        print(display_df.to_string(index=False))

        # 统计分析
        print("\n统计分析：")
        print(f"概念板块总数：{len(concept_df)}")
        print(f"{concept_name} 成分股数量：{len(constituents_df)}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：数据可能暂时不可用，请稍后重试")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("资金流数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_track_stock_fund_flow()
    scenario_2_analyze_sector_rotation()
    scenario_3_main_fund_ranking()
    scenario_4_industry_sectors()
    scenario_5_concept_sectors()
    scenario_6_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_6_multi_source_example():
    """场景 6：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 6：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = FundFlowFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = FundFlowFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")

        # 通过 provider 获取数据
        df = sina_provider.get_stock_fund_flow(symbol, start_date, end_date)

        if df.empty:
            print("无资金流数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
