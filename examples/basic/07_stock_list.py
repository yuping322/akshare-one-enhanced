#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 7：获取股票列表

本示例展示如何使用 akshare-one 获取A股股票列表，包括：
- 获取全部A股实时行情数据
- 按市场筛选（沪市/深市/科创板/创业板）
- 按行业板块筛选
- 导出股票列表到CSV文件

运行方式：
    python examples/basic/07_stock_list.py
"""

import os
import pandas as pd
from datetime import datetime
from akshare_one import (
    get_realtime_data,
    get_industry_list,
    get_industry_stocks,
    get_kcb_stocks,
    get_cyb_stocks,
)


def example_get_all_stocks():
    """场景1：获取全部A股列表"""
    print("\n" + "=" * 60)
    print("场景1：获取全部A股股票列表")
    print("=" * 60)

    try:
        df = get_realtime_data(source="eastmoney")

        if df.empty:
            print("\n警告: 未获取到数据，请检查网络连接或数据源")
            return None

        print(f"\n获取到 {len(df)} 只A股股票")
        print("\n数据列包含：")
        print("  - symbol: 股票代码")
        print("  - price: 最新价")
        print("  - change: 涨跌额")
        print("  - pct_change: 涨跌幅(%)")
        print("  - volume: 成交量(手)")
        print("  - amount: 成交额(元)")

        print("\n前10只股票：")
        print(df.head(10).to_string(index=False))

        return df

    except Exception as e:
        print(f"\n错误: 获取股票列表失败 - {e}")
        return None


def example_filter_by_market(df_all=None):
    """场景2：按市场筛选"""
    print("\n" + "=" * 60)
    print("场景2：按市场筛选股票")
    print("=" * 60)

    if df_all is None or df_all.empty:
        print("\n提示: 需要先获取全市场数据，正在重新获取...")
        df_all = get_realtime_data(source="eastmoney")

    if df_all.empty:
        print("\n错误: 无法获取数据")
        return

    # 沪市股票（代码以6开头）
    df_sh = df_all[df_all["symbol"].str.startswith("6")]
    print(f"\n沪市股票数量: {len(df_sh)}")

    # 深市股票（代码以0或3开头）
    df_sz = df_all[df_all["symbol"].str.startswith(("0", "3"))]
    print(f"深市股票数量: {len(df_sz)}")

    # 科创板股票（代码以688开头）
    try:
        df_kcb = get_kcb_stocks(source="eastmoney")
        if not df_kcb.empty:
            print(f"科创板股票数量: {len(df_kcb)}")
            print("\n科创板前5只股票：")
            print(df_kcb.head(5).to_string(index=False))
        else:
            print("科创板股票数据为空")
    except Exception as e:
        print(f"获取科创板数据失败: {e}")

    # 创业板股票（代码以30开头）
    try:
        df_cyb = get_cyb_stocks(source="eastmoney")
        if not df_cyb.empty:
            print(f"\n创业板股票数量: {len(df_cyb)}")
            print("\n创业板前5只股票：")
            print(df_cyb.head(5).to_string(index=False))
        else:
            print("创业板股票数据为空")
    except Exception as e:
        print(f"获取创业板数据失败: {e}")


def example_filter_by_industry():
    """场景3：按行业筛选"""
    print("\n" + "=" * 60)
    print("场景3：按行业板块筛选股票")
    print("=" * 60)

    try:
        # 获取行业列表
        df_industries = get_industry_list(source="eastmoney")

        if df_industries.empty:
            print("\n错误: 未获取到行业列表")
            return

        print(f"\n获取到 {len(df_industries)} 个行业板块")
        print("\n行业板块列表（前10个）：")
        print(df_industries.head(10).to_string(index=False))

        # 选择几个示例行业获取股票
        example_industries = ["白酒", "半导体", "银行"]

        for industry_name in example_industries:
            try:
                print(f"\n\n行业：{industry_name}")
                df_stocks = get_industry_stocks(industry_name, source="eastmoney")

                if df_stocks.empty:
                    print(f"  未找到该行业的股票数据")
                    continue

                print(f"  股票数量: {len(df_stocks)}")
                print(f"  前5只股票：")
                print(df_stocks.head(5).to_string(index=False))

            except Exception as e:
                print(f"  获取行业'{industry_name}'股票失败: {e}")

    except Exception as e:
        print(f"\n错误: 获取行业列表失败 - {e}")


def example_export_to_csv(df_all=None):
    """场景4：导出股票列表到CSV"""
    print("\n" + "=" * 60)
    print("场景4：导出股票列表到CSV")
    print("=" * 60)

    if df_all is None or df_all.empty:
        print("\n提示: 需要先获取全市场数据，正在重新获取...")
        df_all = get_realtime_data(source="eastmoney")

    if df_all.empty:
        print("\n错误: 无法获取数据，导出失败")
        return

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 格式化数据
    df_export = df_all.copy()
    df_export["export_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 添加市场分类列
    df_export["market"] = df_export["symbol"].apply(
        lambda x: "科创板"
        if x.startswith("688")
        else "创业板"
        if x.startswith("30")
        else "深市"
        if x.startswith(("0", "3"))
        else "沪市"
        if x.startswith("6")
        else "其他"
    )

    # 按涨跌幅排序
    df_sorted = df_export.sort_values("pct_change", ascending=False)

    # 重命名列（中文）
    df_formatted = df_sorted.rename(
        columns={
            "symbol": "股票代码",
            "price": "最新价",
            "change": "涨跌额",
            "pct_change": "涨跌幅(%)",
            "open": "今开",
            "high": "最高",
            "low": "最低",
            "prev_close": "昨收",
            "volume": "成交量(手)",
            "amount": "成交额(元)",
            "market": "市场",
            "export_time": "导出时间",
        }
    )

    # 导出全部A股
    filename_all = f"{output_dir}/all_stocks_{datetime.now().strftime('%Y%m%d')}.csv"
    df_formatted.to_csv(filename_all, index=False, encoding="utf-8-sig")
    print(f"\n全部A股列表已导出到: {filename_all}")
    print(f"  股票总数: {len(df_formatted)}")

    # 按市场分别导出
    markets = ["沪市", "深市", "创业板", "科创板"]
    for market in markets:
        df_market = df_formatted[df_formatted["市场"] == market]
        if not df_market.empty:
            filename_market = f"{output_dir}/{market}_stocks_{datetime.now().strftime('%Y%m%d')}.csv"
            df_market.to_csv(filename_market, index=False, encoding="utf-8-sig")
            print(f"  {market}股票已导出到: {filename_market} ({len(df_market)}只)")

    # 导出涨幅前50
    df_top50 = df_formatted.head(50)
    filename_top = f"{output_dir}/top50_gainers_{datetime.now().strftime('%Y%m%d')}.csv"
    df_top50.to_csv(filename_top, index=False, encoding="utf-8-sig")
    print(f"\n涨幅前50股票已导出到: {filename_top}")

    # 导出跌幅前50
    df_bottom50 = df_formatted.tail(50)
    filename_bottom = f"{output_dir}/top50_losers_{datetime.now().strftime('%Y%m%d')}.csv"
    df_bottom50.to_csv(filename_bottom, index=False, encoding="utf-8-sig")
    print(f"跌幅前50股票已导出到: {filename_bottom}")

    print("\n导出完成！")


def example_statistics(df_all=None):
    """额外场景：统计分析"""
    print("\n" + "=" * 60)
    print("额外场景：市场统计分析")
    print("=" * 60)

    if df_all is None or df_all.empty:
        print("\n提示: 需要先获取全市场数据，正在重新获取...")
        df_all = get_realtime_data(source="eastmoney")

    if df_all.empty:
        print("\n错误: 无法获取数据")
        return

    # 统计涨跌分布
    up_count = len(df_all[df_all["pct_change"] > 0])
    down_count = len(df_all[df_all["pct_change"] < 0])
    flat_count = len(df_all[df_all["pct_change"] == 0])

    print(f"\n涨跌分布：")
    print(f"  上涨股票: {up_count} ({up_count / len(df_all) * 100:.1f}%)")
    print(f"  下跌股票: {down_count} ({down_count / len(df_all) * 100:.1f}%)")
    print(f"  平盘股票: {flat_count} ({flat_count / len(df_all) * 100:.1f}%)")

    # 统计涨跌幅分布
    limit_up = len(df_all[df_all["pct_change"] >= 9.9])
    limit_down = len(df_all[df_all["pct_change"] <= -9.9])

    print(f"\n涨跌停统计：")
    print(f"  涨停股票: {limit_up}")
    print(f"  跌停股票: {limit_down}")

    # 市场概况
    avg_change = df_all["pct_change"].mean()
    max_up = df_all["pct_change"].max()
    max_down = df_all["pct_change"].min()

    print(f"\n市场概况：")
    print(f"  平均涨跌幅: {avg_change:.2f}%")
    print(f"  最大涨幅: {max_up:.2f}%")
    print(f"  最大跌幅: {max_down:.2f}%")

    # 涨幅前10
    print(f"\n涨幅前10股票：")
    df_top10 = df_all.nlargest(10, "pct_change")
    print(df_top10[["symbol", "price", "pct_change"]].to_string(index=False))

    # 跌幅前10
    print(f"\n跌幅前10股票：")
    df_bottom10 = df_all.nsmallest(10, "pct_change")
    print(df_bottom10[["symbol", "price", "pct_change"]].to_string(index=False))


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 股票列表查询示例")
    print("=" * 60)

    # 先获取全市场数据，后续场景可以复用
    print("\n提示: 正在获取全市场数据...")
    df_all = example_get_all_stocks()

    # 运行其他场景
    example_filter_by_market(df_all)
    example_filter_by_industry()
    example_export_to_csv(df_all)
    example_statistics(df_all)

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
    print("\n实用提示：")
    print("1. 使用 get_realtime_data() 不传参数可获取全市场数据")
    print("2. 使用股票代码前缀规则可快速筛选市场")
    print("3. 使用 get_industry_stocks() 可获取指定行业的股票")
    print("4. 导出数据前建议先排序和格式化，提高可读性")


if __name__ == "__main__":
    main()
