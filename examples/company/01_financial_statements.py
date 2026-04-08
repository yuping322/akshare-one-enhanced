#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司财务报表示例 1：获取财务报表数据

本示例展示如何使用 akshare-one 获取公司财务报表数据，包括：
- 获取资产负债表
- 获取利润表
- 获取现金流量表
- 财务指标计算与分析

运行方式：
    python examples/company/01_financial_statements.py

注意：本示例仅供学习参考，不构成投资建议
"""

import os
import pandas as pd
from akshare_one import (
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_financial_metrics,
)


def example_balance_sheet():
    """示例1：获取资产负债表"""
    print("\n" + "=" * 60)
    print("示例1：获取资产负债表")
    print("=" * 60)

    # 获取资产负债表数据
    df = get_balance_sheet(symbol="600519", source="sina")

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    print(f"\n获取到 {len(df)} 条资产负债表数据")
    print("\n最近3期资产负债表主要数据：")
    print(df.head(3).to_string(index=False))

    # 分析资产负债表关键指标
    if not df.empty:
        print("\n资产负债表关键指标分析：")
        latest = df.iloc[0]

        # 资产负债率 = 负债合计 / 资产总计
        if "total_assets" in latest and "total_liabilities" in latest:
            total_assets = latest["total_assets"]
            total_liabilities = latest["total_liabilities"]
            if pd.notna(total_assets) and pd.notna(total_liabilities) and total_assets != 0:
                debt_ratio = (total_liabilities / total_assets) * 100
                print(f"  资产负债率: {debt_ratio:.2f}%")

        # 流动比率 = 流动资产 / 流动负债
        if "total_current_assets" in latest and "total_current_liabilities" in latest:
            current_assets = latest["total_current_assets"]
            current_liabilities = latest["total_current_liabilities"]
            if pd.notna(current_assets) and pd.notna(current_liabilities) and current_liabilities != 0:
                current_ratio = current_assets / current_liabilities
                print(f"  流动比率: {current_ratio:.2f}")

        # 总资产
        if "total_assets" in latest and pd.notna(latest["total_assets"]):
            print(f"  总资产: {latest['total_assets']:,.2f} 元")

        # 净资产
        if "total_equity" in latest and pd.notna(latest["total_equity"]):
            print(f"  净资产: {latest['total_equity']:,.2f} 元")


def example_income_statement():
    """示例2：获取利润表"""
    print("\n" + "=" * 60)
    print("示例2：获取利润表")
    print("=" * 60)

    # 获取利润表数据
    df = get_income_statement(symbol="600519", source="sina")

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    print(f"\n获取到 {len(df)} 条利润表数据")
    print("\n最近3期利润表主要数据：")
    print(df.head(3).to_string(index=False))

    # 分析利润表关键指标
    if not df.empty:
        print("\n利润表关键指标分析：")
        latest = df.iloc[0]
        previous = df.iloc[1] if len(df) > 1 else None

        # 营业收入
        if "operating_revenue" in latest and pd.notna(latest["operating_revenue"]):
            print(f"  营业收入: {latest['operating_revenue']:,.2f} 元")
            if (
                previous is not None
                and "operating_revenue" in previous
                and pd.notna(previous["operating_revenue"])
                and previous["operating_revenue"] != 0
            ):
                growth = (
                    (latest["operating_revenue"] - previous["operating_revenue"]) / previous["operating_revenue"] * 100
                )
                print(f"  营业收入同比增长: {growth:.2f}%")

        # 净利润
        if "net_profit" in latest and pd.notna(latest["net_profit"]):
            print(f"  净利润: {latest['net_profit']:,.2f} 元")
            if (
                previous is not None
                and "net_profit" in previous
                and pd.notna(previous["net_profit"])
                and previous["net_profit"] != 0
            ):
                growth = (latest["net_profit"] - previous["net_profit"]) / previous["net_profit"] * 100
                print(f"  净利润同比增长: {growth:.2f}%")

        # 毛利率 = (营业收入 - 营业成本) / 营业收入
        if "operating_revenue" in latest and "operating_cost" in latest:
            if (
                pd.notna(latest["operating_revenue"])
                and pd.notna(latest["operating_cost"])
                and latest["operating_revenue"] != 0
            ):
                gross_margin = (
                    (latest["operating_revenue"] - latest["operating_cost"]) / latest["operating_revenue"] * 100
                )
                print(f"  毛利率: {gross_margin:.2f}%")

        # 净利率 = 净利润 / 营业收入
        if "net_profit" in latest and "operating_revenue" in latest:
            if (
                pd.notna(latest["net_profit"])
                and pd.notna(latest["operating_revenue"])
                and latest["operating_revenue"] != 0
            ):
                net_margin = latest["net_profit"] / latest["operating_revenue"] * 100
                print(f"  净利率: {net_margin:.2f}%")


def example_cash_flow():
    """示例3：获取现金流量表"""
    print("\n" + "=" * 60)
    print("示例3：获取现金流量表")
    print("=" * 60)

    # 获取现金流量表数据
    df = get_cash_flow(symbol="600519", source="sina")

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    print(f"\n获取到 {len(df)} 条现金流量表数据")
    print("\n最近3期现金流量表主要数据：")
    print(df.head(3).to_string(index=False))

    # 分析现金流量表关键指标
    if not df.empty:
        print("\n现金流量表关键指标分析：")
        latest = df.iloc[0]

        # 经营活动现金流
        if "net_cash_flow_from_operations" in latest and pd.notna(latest["net_cash_flow_from_operations"]):
            ocf = latest["net_cash_flow_from_operations"]
            print(f"  经营活动现金流量净额: {ocf:,.2f} 元")

        # 投资活动现金流
        if "net_cash_flow_from_investing" in latest and pd.notna(latest["net_cash_flow_from_investing"]):
            icf = latest["net_cash_flow_from_investing"]
            print(f"  投资活动现金流量净额: {icf:,.2f} 元")

        # 筹资活动现金流
        if "net_cash_flow_from_financing" in latest and pd.notna(latest["net_cash_flow_from_financing"]):
            fcf = latest["net_cash_flow_from_financing"]
            print(f"  筹资活动现金流量净额: {fcf:,.2f} 元")

        # 现金及现金等价物净增加额
        if "change_in_cash_and_equivalents" in latest and pd.notna(latest["change_in_cash_and_equivalents"]):
            cash_change = latest["change_in_cash_and_equivalents"]
            print(f"  现金及现金等价物净增加额: {cash_change:,.2f} 元")

        # 期末现金及现金等价物余额
        if "ending_cash_balance" in latest and pd.notna(latest["ending_cash_balance"]):
            cash_balance = latest["ending_cash_balance"]
            print(f"  期末现金及现金等价物余额: {cash_balance:,.2f} 元")


def example_financial_analysis():
    """示例4：综合财务分析"""
    print("\n" + "=" * 60)
    print("示例4：综合财务分析与指标计算")
    print("=" * 60)

    symbol = "600519"

    # 获取财务指标数据
    print(f"\n获取股票 {symbol} 的财务指标...")
    try:
        df_metrics = get_financial_metrics(symbol=symbol, source="eastmoney_direct")
        if not df_metrics.empty:
            print(f"\n获取到 {len(df_metrics)} 条财务指标数据")
            print("\n最近3期财务指标：")
            print(df_metrics.head(3).to_string(index=False))
        else:
            print("\n获取到的财务指标数据为空")
    except Exception as e:
        print(f"获取财务指标失败: {e}")
        print("\n使用三大报表数据进行综合分析...")

    # 获取三大报表数据进行综合分析
    print("\n" + "-" * 60)
    print("综合财务分析：")
    print("-" * 60)

    try:
        df_balance = get_balance_sheet(symbol=symbol, source="sina")
        df_income = get_income_statement(symbol=symbol, source="sina")
        df_cashflow = get_cash_flow(symbol=symbol, source="sina")
    except Exception as e:
        print(f"获取财务数据失败: {e}")
        return

    if df_balance.empty or df_income.empty or df_cashflow.empty:
        print("财务数据不完整，无法进行综合分析")
        return

    # 取最近3期数据进行分析
    print("\n近3期财务数据对比分析：")

    for i in range(min(3, len(df_balance))):
        if i >= len(df_income) or i >= len(df_cashflow):
            break
        balance = df_balance.iloc[i]
        income = df_income.iloc[i]
        cashflow = df_cashflow.iloc[i]

        report_date = balance.get("report_date", f"第{i + 1}期")
        print(f"\n{report_date}:")

        # 盈利能力分析
        if "operating_revenue" in income and "net_profit" in income:
            if (
                pd.notna(income["operating_revenue"])
                and pd.notna(income["net_profit"])
                and income["operating_revenue"] != 0
            ):
                net_margin = income["net_profit"] / income["operating_revenue"] * 100
                print(f"  净利率: {net_margin:.2f}%")

        # 偿债能力分析
        if "total_assets" in balance and "total_liabilities" in balance:
            if (
                pd.notna(balance["total_assets"])
                and pd.notna(balance["total_liabilities"])
                and balance["total_assets"] != 0
            ):
                debt_ratio = balance["total_liabilities"] / balance["total_assets"] * 100
                print(f"  资产负债率: {debt_ratio:.2f}%")

        # 现金流质量分析
        if "net_profit" in income and "net_cash_flow_from_operations" in cashflow:
            if (
                pd.notna(income["net_profit"])
                and pd.notna(cashflow["net_cash_flow_from_operations"])
                and income["net_profit"] != 0
            ):
                ocf_to_ni = cashflow["net_cash_flow_from_operations"] / income["net_profit"]
                print(f"  经营现金流/净利润: {ocf_to_ni:.2f}")
                if ocf_to_ni > 1:
                    print("    (现金流质量良好)")
                else:
                    print("    (需关注现金流质量)")

    # ROE分析（净资产收益率）
    print("\n净资产收益率(ROE)分析：")
    for i in range(min(3, len(df_balance))):
        if i >= len(df_income):
            break
        balance = df_balance.iloc[i]
        income = df_income.iloc[i]

        if "net_profit" in income and "total_equity" in balance:
            if pd.notna(income["net_profit"]) and pd.notna(balance["total_equity"]) and balance["total_equity"] != 0:
                roe = income["net_profit"] / balance["total_equity"] * 100
                report_date = balance.get("report_date", f"第{i + 1}期")
                print(f"  {report_date} ROE: {roe:.2f}%")


def example_data_filtering():
    """示例5：财务数据筛选与导出"""
    print("\n" + "=" * 60)
    print("示例5：财务数据筛选与导出")
    print("=" * 60)

    # 使用列筛选，只获取特定字段
    print("\n筛选特定列数据（营业收入、净利润）：")
    try:
        df = get_income_statement(
            symbol="600519", source="sina", columns=["report_date", "operating_revenue", "net_profit", "operating_cost"]
        )
        if not df.empty:
            print(f"\n筛选后的数据（{len(df)} 条）：")
            print(df.head(5).to_string(index=False))
        else:
            print("\n警告: 未获取到数据")
    except Exception as e:
        print(f"\n获取或筛选数据失败: {e}")
        return

    # 使用行筛选，筛选特定条件
    print("\n筛选净利润大于100亿的数据：")
    try:
        df_filtered = get_income_statement(
            symbol="600519",
            source="sina",
            row_filter={"net_profit": (">", 10000000000)},  # 100亿
        )
        if not df_filtered.empty:
            print(f"\n筛选后的数据（{len(df_filtered)} 条）：")
            print(df_filtered.head().to_string(index=False))
        else:
            print("\n没有符合条件的数据")
    except Exception as e:
        print(f"\n行筛选失败: {e}")

    # 导出到CSV
    print("\n将财务数据导出到CSV文件...")
    try:
        output_dir = os.path.join("/tmp", "akshare_one", "examples", "financial")
        os.makedirs(output_dir, exist_ok=True)

        df_balance = get_balance_sheet(symbol="600519", source="sina")
        df_income = get_income_statement(symbol="600519", source="sina")
        df_cashflow = get_cash_flow(symbol="600519", source="sina")

        df_balance.to_csv(os.path.join(output_dir, "balance_sheet_600519.csv"), index=False, encoding="utf-8-sig")
        df_income.to_csv(os.path.join(output_dir, "income_statement_600519.csv"), index=False, encoding="utf-8-sig")
        df_cashflow.to_csv(os.path.join(output_dir, "cashflow_600519.csv"), index=False, encoding="utf-8-sig")

        print(f"已导出以下文件到 {output_dir}:")
        print("  - balance_sheet_600519.csv")
        print("  - income_statement_600519.csv")
        print("  - cashflow_600519.csv")
    except Exception as e:
        print(f"\n导出数据失败: {e}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 财务报表数据获取示例")
    print("=" * 60)

    # 运行所有示例
    example_balance_sheet()
    example_income_statement()
    example_cash_flow()
    example_financial_analysis()
    example_data_filtering()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
