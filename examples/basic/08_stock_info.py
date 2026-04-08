#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 8：获取股票基本信息

本示例展示如何使用 akshare-one 获取股票基本信息，包括：
- 查询单个股票基本信息
- 批量查询多只股票信息
- 获取行业和市值信息
- 对比多只股票基本信息

运行方式：
    python examples/basic/08_stock_info.py

注意：本示例需要联网访问东方财富数据源
"""

import pandas as pd
from akshare_one import get_basic_info


def example_single_stock():
    """示例1：查询单个股票基本信息"""
    print("\n" + "=" * 60)
    print("示例1：查询单个股票基本信息")
    print("=" * 60)

    # 获取浦发银行(600000)的基本信息
    try:
        df = get_basic_info(symbol="600000")
    except Exception as e:
        print(f"\n获取数据失败: {e}")
        return

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    print("\n浦发银行(600000)基本信息：")
    print(df.to_string(index=False))

    # 数据字段说明：
    # - price: 最新价
    # - symbol: 股票代码
    # - name: 股票简称
    # - total_shares: 总股本(股)
    # - float_shares: 流通股(股)
    # - total_market_cap: 总市值(元)
    # - float_market_cap: 流通市值(元)
    # - industry: 所属行业
    # - listing_date: 上市时间

    if not df.empty:
        row = df.iloc[0]
        print("\n关键信息摘要：")
        if "name" in row and pd.notna(row["name"]):
            print(f"  股票名称: {row['name']}")
        if "price" in row and pd.notna(row["price"]):
            print(f"  最新价格: {row['price']:.2f} 元")
        if "industry" in row and pd.notna(row["industry"]):
            print(f"  所属行业: {row['industry']}")
        if "total_market_cap" in row and pd.notna(row["total_market_cap"]):
            print(f"  总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
        if "float_market_cap" in row and pd.notna(row["float_market_cap"]):
            print(f"  流通市值: {row['float_market_cap'] / 1e8:.2f} 亿元")
        if "listing_date" in row and pd.notna(row["listing_date"]):
            listing_date = row["listing_date"]
            if hasattr(listing_date, "strftime"):
                print(f"  上市日期: {listing_date}")
            else:
                print(f"  上市日期: {listing_date}")


def example_batch_query():
    """示例2：批量查询多只股票信息"""
    print("\n" + "=" * 60)
    print("示例2：批量查询多只股票信息")
    print("=" * 60)

    # 定义要查询的股票列表
    symbols = ["600000", "000001", "600519", "000858", "600036"]

    # 批量获取基本信息
    results = []
    for symbol in symbols:
        try:
            df = get_basic_info(symbol=symbol)
            if not df.empty:
                results.append(df)
        except Exception as e:
            print(f"  获取 {symbol} 失败: {e}")

    # 合并结果
    if results:
        df_all = pd.concat(results, ignore_index=True)

        print(f"\n成功获取 {len(df_all)} 只股票的信息：")
        print(df_all[["symbol", "name", "price", "industry"]].to_string(index=False))

        # 统计行业分布
        print("\n行业分布：")
        industry_counts = df_all["industry"].value_counts()
        for industry, count in industry_counts.items():
            print(f"  {industry}: {count} 只")


def example_industry_analysis():
    """示例3：获取行业和市值信息"""
    print("\n" + "=" * 60)
    print("示例3：获取行业和市值信息")
    print("=" * 60)

    # 定义不同行业的代表股票
    stocks_by_industry = {
        "银行": ["600000", "601398", "601288"],
        "白酒": ["600519", "000858", "000568"],
        "科技": ["000063", "002415", "300750"],
    }

    print("\n各行业代表股票信息：")

    for industry, symbols in stocks_by_industry.items():
        print(f"\n【{industry}】行业：")

        for symbol in symbols:
            try:
                df = get_basic_info(symbol=symbol)
                if df.empty:
                    print(f"  {symbol}: 未获取到数据")
                    continue
                row = df.iloc[0]
                name = row.get("name", symbol) if "name" in row else symbol
                print(f"  {name}({symbol}):")
                if "price" in row and pd.notna(row["price"]):
                    print(f"    最新价: {row['price']:.2f} 元")
                if "total_market_cap" in row and pd.notna(row["total_market_cap"]):
                    print(f"    总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
                if "float_market_cap" in row and pd.notna(row["float_market_cap"]):
                    print(f"    流通市值: {row['float_market_cap'] / 1e8:.2f} 亿元")
            except Exception as e:
                print(f"  {symbol}: 获取失败 ({e})")


def example_stock_comparison():
    """示例4：对比多只股票基本信息"""
    print("\n" + "=" * 60)
    print("示例4：对比多只股票基本信息")
    print("=" * 60)

    # 定义要对比的股票
    symbols = ["600000", "000001", "600036", "601166"]

    print("\n对比银行股基本信息：")

    # 获取所有股票信息
    results = []
    for symbol in symbols:
        try:
            df = get_basic_info(symbol=symbol)
            if not df.empty:
                results.append(df)
        except Exception as e:
            print(f"  获取 {symbol} 失败: {e}")

    if not results:
        print("\n警告: 未获取到任何股票数据")
        return

    df_all = pd.concat(results, ignore_index=True)

    # 选择对比维度
    available_cols = ["symbol", "name", "price", "total_market_cap", "float_market_cap", "industry", "listing_date"]
    cols_to_use = [col for col in available_cols if col in df_all.columns]
    df_compare = df_all[cols_to_use].copy()

    # 格式化市值显示
    if "total_market_cap" in df_compare.columns:
        df_compare["总市值(亿)"] = df_compare["total_market_cap"] / 1e8
    if "float_market_cap" in df_compare.columns:
        df_compare["流通市值(亿)"] = df_compare["float_market_cap"] / 1e8

    display_cols = ["symbol", "name", "price", "总市值(亿)", "流通市值(亿)"]
    display_cols = [col for col in display_cols if col in df_compare.columns]
    print("\n基本信息对比：")
    print(df_compare[display_cols].to_string(index=False))

    # 计算市值排名
    if "总市值(亿)" in df_compare.columns:
        print("\n市值排名（从大到小）：")
        df_sorted = df_compare.sort_values("总市值(亿)", ascending=False)
        for idx, row in df_sorted.iterrows():
            name = row.get("name", "N/A")
            print(f"  {name}: {row['总市值(亿)']:.2f} 亿元")

    # 计算价格对比
    if "price" in df_compare.columns and not df_compare["price"].isna().all():
        print("\n价格统计：")
        print(f"  平均价格: {df_compare['price'].mean():.2f} 元")
        max_price_row = df_compare[df_compare["price"] == df_compare["price"].max()]
        min_price_row = df_compare[df_compare["price"] == df_compare["price"].min()]
        if not max_price_row.empty and "name" in max_price_row.columns:
            max_name = max_price_row["name"].values[0]
            print(f"  最高价格: {df_compare['price'].max():.2f} 元 ({max_name})")
        if not min_price_row.empty and "name" in min_price_row.columns:
            min_name = min_price_row["name"].values[0]
            print(f"  最低价格: {df_compare['price'].min():.2f} 元 ({min_name})")

    # 上市时间对比
    if "listing_date" in df_compare.columns:
        print("\n上市时间对比：")
        df_sorted_date = df_compare.sort_values("listing_date")
        for idx, row in df_sorted_date.iterrows():
            name = row.get("name", "N/A")
            listing_date = row.get("listing_date", "N/A")
            if hasattr(listing_date, "strftime"):
                print(f"  {name}: {listing_date.strftime('%Y-%m-%d')}")
            else:
                print(f"  {name}: {listing_date}")


def example_format_output():
    """示例5：格式化输出"""
    print("\n" + "=" * 60)
    print("示例5：格式化输出")
    print("=" * 60)

    # 获取单只股票信息
    try:
        df = get_basic_info(symbol="600519")
    except Exception as e:
        print(f"\n获取数据失败: {e}")
        return

    if df.empty:
        print("\n警告: 未获取到数据")
        return

    row = df.iloc[0]

    print("\n贵州茅台(600519)详细信息：")
    print("-" * 40)

    # 格式化输出各项信息
    if "symbol" in row:
        print(f"股票代码: {row['symbol']}")
    if "name" in row and pd.notna(row["name"]):
        print(f"股票名称: {row['name']}")
    if "price" in row and pd.notna(row["price"]):
        print(f"最新价格: {row['price']:.2f} 元")
    if "industry" in row and pd.notna(row["industry"]):
        print(f"所属行业: {row['industry']}")
    if "listing_date" in row and pd.notna(row["listing_date"]):
        listing_date = row["listing_date"]
        if hasattr(listing_date, "strftime"):
            print(f"上市日期: {listing_date.strftime('%Y年%m月%d日')}")
        else:
            print(f"上市日期: {listing_date}")

    if "total_shares" in row and "float_shares" in row:
        if pd.notna(row["total_shares"]) and pd.notna(row["float_shares"]):
            print("\n股本信息：")
            print(f"  总股本: {row['total_shares'] / 1e8:.2f} 亿股")
            print(f"  流通股: {row['float_shares'] / 1e8:.2f} 亿股")
            if row["total_shares"] != 0:
                print(f"  流通比例: {row['float_shares'] / row['total_shares'] * 100:.2f}%")

    if "total_market_cap" in row and pd.notna(row["total_market_cap"]):
        print("\n市值信息：")
        print(f"  总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
    if "float_market_cap" in row and pd.notna(row["float_market_cap"]):
        print(f"  流通市值: {row['float_market_cap'] / 1e8:.2f} 亿元")

    # 添加分隔线
    print("-" * 40)


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 股票基本信息示例")
    print("=" * 60)

    # 运行所有示例
    example_single_stock()
    example_batch_query()
    example_industry_analysis()
    example_stock_comparison()
    example_format_output()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
