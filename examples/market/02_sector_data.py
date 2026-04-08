#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块数据示例

本示例展示如何使用 akshare-one 获取板块数据，包括：
- 行业板块列表
- 概念板块列表
- 板块成分股查询
- 板块涨跌幅排名
- 板块资金流向

运行方式：
    python examples/market/02_sector_data.py
"""

from datetime import datetime, timedelta

from akshare_one import (
    get_industry_list,
    get_industry_stocks,
    get_concept_list,
    get_concept_stocks,
    get_sector_fund_flow,
)
from akshare_one.modules.industry import IndustryFactory
from akshare_one.modules.concept import ConceptFactory


def scenario_1_industry_list():
    """场景1：获取行业板块列表"""
    print("\n" + "=" * 80)
    print("场景1：获取行业板块列表")
    print("=" * 80)

    try:
        print("\n正在获取行业板块列表...")

        # 获取行业板块列表（包含涨跌幅等行情数据）
        df = get_industry_list(source="eastmoney")

        if df.empty:
            print("无行业板块数据返回")
            return

        # 显示前15个行业板块
        print("\n行业板块列表（前15个）：")
        display_cols = ["rank", "name", "code", "pct_change", "up_count", "down_count", "leading_stock"]
        available_cols = [c for c in display_cols if c in df.columns]
        print(df.head(15)[available_cols].to_string(index=False))

        # 统计信息
        print("\n统计分析：")
        print(f"行业板块总数：{len(df)}")
        if "pct_change" in df.columns:
            up_sectors = len(df[df["pct_change"] > 0])
            down_sectors = len(df[df["pct_change"] < 0])
            print(f"上涨板块数：{up_sectors}")
            print(f"下跌板块数：{down_sectors}")
            if len(df) > 0:
                top_gainer = df.loc[df["pct_change"].idxmax()]
                top_loser = df.loc[df["pct_change"].idxmin()]
                print(f"涨幅最大板块：{top_gainer['name']} ({top_gainer['pct_change']:.2f}%)")
                print(f"跌幅最大板块：{top_loser['name']} ({top_loser['pct_change']:.2f}%)")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_concept_list():
    """场景2：获取概念板块列表"""
    print("\n" + "=" * 80)
    print("场景2：获取概念板块列表")
    print("=" * 80)

    try:
        print("\n正在获取概念板块列表...")

        # 获取概念板块列表（包含涨跌幅等行情数据）
        df = get_concept_list(source="eastmoney")

        if df.empty:
            print("无概念板块数据返回")
            return

        # 显示前15个概念板块
        print("\n概念板块列表（前15个）：")
        display_cols = ["rank", "name", "code", "pct_change", "up_count", "down_count", "leading_stock"]
        available_cols = [c for c in display_cols if c in df.columns]
        print(df.head(15)[available_cols].to_string(index=False))

        # 统计信息
        print("\n统计分析：")
        print(f"概念板块总数：{len(df)}")
        if "pct_change" in df.columns:
            up_concepts = len(df[df["pct_change"] > 0])
            down_concepts = len(df[df["pct_change"] < 0])
            print(f"上涨概念数：{up_concepts}")
            print(f"下跌概念数：{down_concepts}")
            if len(df) > 0:
                top_gainer = df.loc[df["pct_change"].idxmax()]
                top_loser = df.loc[df["pct_change"].idxmin()]
                print(f"涨幅最大概念：{top_gainer['name']} ({top_gainer['pct_change']:.2f}%)")
                print(f"跌幅最大概念：{top_loser['name']} ({top_loser['pct_change']:.2f}%)")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_sector_constituents():
    """场景3：查询板块成分股"""
    print("\n" + "=" * 80)
    print("场景3：查询板块成分股")
    print("=" * 80)

    try:
        # 先获取一个行业板块
        print("\n获取行业板块成分股示例：")
        industry_df = get_industry_list(source="eastmoney")

        if not industry_df.empty:
            # 选择第一个行业
            first_industry = industry_df.iloc[0]
            industry_name = first_industry["name"]
            print(f"\n查询行业：{industry_name}")

            # 获取行业成分股
            stocks_df = get_industry_stocks(industry_name, source="eastmoney")

            if not stocks_df.empty:
                print(f"\n{industry_name} 成分股（前10只）：")
                display_cols = ["symbol", "name", "price", "pct_change", "turnover"]
                available_cols = [c for c in display_cols if c in stocks_df.columns]
                print(stocks_df.head(10)[available_cols].to_string(index=False))
                print(f"\n成分股总数：{len(stocks_df)}")

        # 获取概念板块成分股
        print("\n" + "-" * 40)
        print("获取概念板块成分股示例：")
        concept_df = get_concept_list(source="eastmoney")

        if not concept_df.empty:
            # 选择第一个概念
            first_concept = concept_df.iloc[0]
            concept_name = first_concept["name"]
            print(f"\n查询概念：{concept_name}")

            # 获取概念成分股
            stocks_df = get_concept_stocks(concept_name, source="eastmoney")

            if not stocks_df.empty:
                print(f"\n{concept_name} 成分股（前10只）：")
                display_cols = ["symbol", "name", "price", "pct_change", "turnover"]
                available_cols = [c for c in display_cols if c in stocks_df.columns]
                print(stocks_df.head(10)[available_cols].to_string(index=False))
                print(f"\n成分股总数：{len(stocks_df)}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_sector_ranking():
    """场景4：板块涨跌幅排名"""
    print("\n" + "=" * 80)
    print("场景4：板块涨跌幅排名")
    print("=" * 80)

    try:
        # 行业板块涨跌幅排名
        print("\n【行业板块涨跌幅排名】")
        print("-" * 40)

        industry_df = get_industry_list(source="eastmoney")

        if not industry_df.empty and "pct_change" in industry_df.columns:
            # 按涨跌幅排序
            sorted_df = industry_df.sort_values("pct_change", ascending=False)

            # 涨幅前10
            print("\n涨幅前10行业板块：")
            display_cols = ["name", "pct_change", "up_count", "down_count", "leading_stock"]
            available_cols = [c for c in display_cols if c in sorted_df.columns]
            print(sorted_df.head(10)[available_cols].to_string(index=False))

            # 跌幅前10
            print("\n跌幅前10行业板块：")
            print(sorted_df.tail(10)[available_cols].to_string(index=False))

        # 概念板块涨跌幅排名
        print("\n【概念板块涨跌幅排名】")
        print("-" * 40)

        concept_df = get_concept_list(source="eastmoney")

        if not concept_df.empty and "pct_change" in concept_df.columns:
            # 按涨跌幅排序
            sorted_df = concept_df.sort_values("pct_change", ascending=False)

            # 涨幅前10
            print("\n涨幅前10概念板块：")
            display_cols = ["name", "pct_change", "up_count", "down_count", "leading_stock"]
            available_cols = [c for c in display_cols if c in sorted_df.columns]
            print(sorted_df.head(10)[available_cols].to_string(index=False))

            # 跌幅前10
            print("\n跌幅前10概念板块：")
            print(sorted_df.tail(10)[available_cols].to_string(index=False))

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_5_sector_fund_flow():
    """场景5：板块资金流向"""
    print("\n" + "=" * 80)
    print("场景5：板块资金流向")
    print("=" * 80)

    try:
        # 设置日期范围（最近7天）
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        # 行业板块资金流向
        print("\n【行业板块资金流向】")
        print(f"时间范围：{start_date} 至 {end_date}")
        print("-" * 40)

        df = get_sector_fund_flow(sector_type="industry", start_date=start_date, end_date=end_date, source="eastmoney")

        if not df.empty:
            # 按主力净流入排序
            if "main_net_inflow" in df.columns:
                sorted_df = df.sort_values("main_net_inflow", ascending=False)

                # 资金流入前10
                print("\n资金流入前10行业板块：")
                display_cols = ["sector_name", "main_net_inflow", "pct_change", "leading_stock"]
                available_cols = [c for c in display_cols if c in sorted_df.columns]
                print(sorted_df.head(10)[available_cols].to_string(index=False))

                # 资金流出前10
                print("\n资金流出前10行业板块：")
                print(sorted_df.tail(10)[available_cols].to_string(index=False))

                # 统计
                total_inflow = df["main_net_inflow"].sum()
                inflow_count = len(df[df["main_net_inflow"] > 0])
                outflow_count = len(df[df["main_net_inflow"] < 0])

                print("\n统计分析：")
                print(f"主力资金净流入总额：{total_inflow:,.2f} 万元")
                print(f"资金流入板块数：{inflow_count}")
                print(f"资金流出板块数：{outflow_count}")
        else:
            print("无行业板块资金流数据")

        # 概念板块资金流向
        print("\n【概念板块资金流向】")
        print(f"时间范围：{start_date} 至 {end_date}")
        print("-" * 40)

        df = get_sector_fund_flow(sector_type="concept", start_date=start_date, end_date=end_date, source="eastmoney")

        if not df.empty:
            if "main_net_inflow" in df.columns:
                sorted_df = df.sort_values("main_net_inflow", ascending=False)

                print("\n资金流入前10概念板块：")
                display_cols = ["sector_name", "main_net_inflow", "pct_change", "leading_stock"]
                available_cols = [c for c in display_cols if c in sorted_df.columns]
                print(sorted_df.head(10)[available_cols].to_string(index=False))

                print("\n资金流出前10概念板块：")
                print(sorted_df.tail(10)[available_cols].to_string(index=False))
        else:
            print("无概念板块资金流数据")

    except Exception as e:
        print(f"发生错误：{e}")


def show_available_sources():
    """显示可用的数据源"""
    print("\n" + "=" * 80)
    print("可用数据源")
    print("=" * 80)

    print("\n行业板块数据源：")
    industry_sources = IndustryFactory.list_sources()
    for source in industry_sources:
        print(f"  - {source}")

    print("\n概念板块数据源：")
    concept_sources = ConceptFactory.list_sources()
    for source in concept_sources:
        print(f"  - {source}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("板块数据示例程序")
    print("=" * 80)

    # 显示可用数据源
    show_available_sources()

    # 运行所有场景
    scenario_1_industry_list()
    scenario_2_concept_list()
    scenario_3_sector_constituents()
    scenario_4_sector_ranking()
    scenario_5_sector_fund_flow()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
