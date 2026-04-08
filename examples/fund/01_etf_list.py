#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金示例 1：获取ETF基金列表

本示例展示如何使用 akshare-one 获取和分析ETF基金列表数据，包括：
- 获取全部ETF列表
- 按类型筛选ETF
- 查询ETF规模排名
- 查询ETF成交额排名
- 导出ETF列表

运行方式：
    python examples/fund/01_etf_list.py
"""

import pandas as pd
from akshare_one import get_etf_list, get_etf_realtime_data


def example_get_all_etf_list():
    """场景1：获取全部ETF列表"""
    print("\n" + "=" * 60)
    print("场景1：获取全部ETF列表")
    print("=" * 60)

    try:
        df = get_etf_list(source="eastmoney")

        if df.empty:
            print("未获取到ETF数据")
            return None

        print(f"\n获取到 {len(df)} 只ETF基金")
        print("\n前10只ETF：")
        print(df.head(10).to_string(index=False))

        return df
    except Exception as e:
        print(f"获取ETF列表失败：{e}")
        print("提示：请检查网络连接或稍后重试")
        return None


def example_filter_etf_by_type():
    """场景2：按类型筛选ETF"""
    print("\n" + "=" * 60)
    print("场景2：按类型筛选ETF")
    print("=" * 60)

    try:
        df = get_etf_realtime_data(source="eastmoney")

        if df.empty:
            print("未获取到ETF数据")
            return

        print("\n原始数据包含字段：")
        print(df.columns.tolist())

        stock_keywords = ["沪深", "中证", "上证", "深证", "创业板", "科创板", "国企", "央企", "红利"]

        stock_df = df[df["name"].str.contains("|".join(stock_keywords), na=False)]
        print(f"\n股票型ETF（示例，共{len(stock_df)}只）：")
        print(stock_df.head(10).to_string(index=False))

        bond_keywords = ["国债", "地方债", "企业债", "公司债", "可转债", "债券"]
        bond_df = df[df["name"].str.contains("|".join(bond_keywords), na=False)]
        print(f"\n债券型ETF（共{len(bond_df)}只）：")
        print(bond_df.head(10).to_string(index=False))

        money_keywords = ["货币", "银华", "华宝"]
        money_df = df[df["name"].str.contains("|".join(money_keywords), na=False)]
        print(f"\n货币型ETF（共{len(money_df)}只）：")
        print(money_df.head(10).to_string(index=False))
    except Exception as e:
        print(f"筛选ETF失败：{e}")
        print("提示：请检查网络连接或稍后重试")


def example_etf_scale_ranking():
    """场景3：查询ETF规模排名"""
    print("\n" + "=" * 60)
    print("场景3：查询ETF规模排名（按成交额）")
    print("=" * 60)

    try:
        df = get_etf_realtime_data(source="eastmoney")

        if df.empty:
            print("未获取到ETF数据")
            return None

        if "amount" not in df.columns:
            print("数据中不包含成交额字段")
            return None

        df_sorted = df.sort_values(by="amount", ascending=False)

        print("\n规模排名TOP 20 ETF（按成交额）：")
        top20 = df_sorted.head(20)[["symbol", "name", "amount", "pct_change", "turnover"]]
        print(top20.to_string(index=False))

        print(f"\n总成交额：{df['amount'].sum():,.2f} 万元")
        print(f"平均成交额：{df['amount'].mean():,.2f} 万元")

        return df_sorted
    except Exception as e:
        print(f"查询ETF规模排名失败：{e}")
        print("提示：请检查网络连接或稍后重试")
        return None


def example_etf_volume_ranking():
    """场景4：查询ETF成交额排名"""
    print("\n" + "=" * 60)
    print("场景4：查询ETF成交额排名")
    print("=" * 60)

    try:
        df = get_etf_realtime_data(source="eastmoney")

        if df.empty:
            print("未获取到ETF数据")
            return None

        if "amount" not in df.columns:
            print("数据中不包含成交额字段")
            return None

        df_sorted = df.sort_values(by="amount", ascending=False).reset_index(drop=True)
        df_sorted["排名"] = df_sorted.index + 1

        print("\n成交额排名TOP 20 ETF：")
        top20 = df_sorted.head(20)[["排名", "symbol", "name", "amount", "volume", "pct_change"]]
        print(top20.to_string(index=False))

        print(f"\n前10名成交额占比：{df_sorted.head(10)['amount'].sum() / df_sorted['amount'].sum() * 100:.2f}%")

        amount_threshold = df["amount"].quantile(0.9)
        hot_etfs = df_sorted[df_sorted["amount"] >= amount_threshold]
        print(f"\n活跃ETF（成交额前10%）：{len(hot_etfs)} 只")
        print(hot_etfs[["排名", "symbol", "name", "amount", "pct_change"]].head(10).to_string(index=False))

        return df_sorted
    except Exception as e:
        print(f"查询ETF成交额排名失败：{e}")
        print("提示：请检查网络连接或稍后重试")
        return None


def example_export_etf_list():
    """场景5：导出ETF列表"""
    print("\n" + "=" * 60)
    print("场景5：导出ETF列表")
    print("=" * 60)

    try:
        df_list = get_etf_list(source="eastmoney")
        df_realtime = get_etf_realtime_data(source="eastmoney")

        if df_list.empty or df_realtime.empty:
            print("未获取到ETF数据")
            return

        df_merged = pd.merge(
            df_list,
            df_realtime[["symbol", "price", "pct_change", "amount", "volume", "turnover"]],
            on="symbol",
            how="left",
        )

        output_file = "etf_list_export.csv"
        df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"\n已导出ETF列表到文件：{output_file}")
        print(f"共导出 {len(df_merged)} 条记录")
        print("\n数据预览（前5条）：")
        print(df_merged.head().to_string(index=False))

        print("\n数据统计：")
        print(f"  - 总ETF数量：{len(df_merged)}")
        print(f"  - 平均价格：{df_merged['price'].mean():.3f}")
        print(f"  - 平均涨跌幅：{df_merged['pct_change'].mean():.2f}%")
        print(f"  - 总成交额：{df_merged['amount'].sum():,.2f} 万元")
    except Exception as e:
        print(f"导出ETF列表失败：{e}")
        print("提示：请检查网络连接或稍后重试")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one ETF基金列表示例")
    print("=" * 60)

    example_get_all_etf_list()
    example_filter_etf_by_type()
    example_etf_scale_ranking()
    example_etf_volume_ranking()
    example_export_etf_list()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
