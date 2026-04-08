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
    df = get_basic_info(symbol="600000")

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
        print(f"  股票名称: {row['name']}")
        print(f"  最新价格: {row['price']:.2f} 元")
        print(f"  所属行业: {row['industry']}")
        print(f"  总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
        print(f"  流通市值: {row['float_market_cap'] / 1e8:.2f} 亿元")
        print(f"  上市日期: {row['listing_date']}")


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
                if not df.empty:
                    row = df.iloc[0]
                    print(f"  {row['name']}({symbol}):")
                    print(f"    最新价: {row['price']:.2f} 元")
                    print(f"    总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
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

    if results:
        df_all = pd.concat(results, ignore_index=True)

        # 选择对比维度
        df_compare = df_all[
            ["symbol", "name", "price", "total_market_cap", "float_market_cap", "industry", "listing_date"]
        ].copy()

        # 格式化市值显示
        df_compare["总市值(亿)"] = df_compare["total_market_cap"] / 1e8
        df_compare["流通市值(亿)"] = df_compare["float_market_cap"] / 1e8

        print("\n基本信息对比：")
        print(df_compare[["symbol", "name", "price", "总市值(亿)", "流通市值(亿)"]].to_string(index=False))

        # 计算市值排名
        print("\n市值排名（从大到小）：")
        df_sorted = df_compare.sort_values("总市值(亿)", ascending=False)
        for idx, row in df_sorted.iterrows():
            print(f"  {row['name']}: {row['总市值(亿)']:.2f} 亿元")

        # 计算价格对比
        print("\n价格统计：")
        print(f"  平均价格: {df_compare['price'].mean():.2f} 元")
        print(
            f"  最高价格: {df_compare['price'].max():.2f} 元 ({df_compare[df_compare['price'] == df_compare['price'].max()]['name'].values[0]})"
        )
        print(
            f"  最低价格: {df_compare['price'].min():.2f} 元 ({df_compare[df_compare['price'] == df_compare['price'].min()]['name'].values[0]})"
        )

        # 上市时间对比
        print("\n上市时间对比：")
        df_sorted_date = df_compare.sort_values("listing_date")
        for idx, row in df_sorted_date.iterrows():
            print(f"  {row['name']}: {row['listing_date'].strftime('%Y-%m-%d')}")


def example_format_output():
    """示例5：格式化输出"""
    print("\n" + "=" * 60)
    print("示例5：格式化输出")
    print("=" * 60)

    # 获取单只股票信息
    df = get_basic_info(symbol="600519")

    if not df.empty:
        row = df.iloc[0]

        print("\n贵州茅台(600519)详细信息：")
        print("-" * 40)

        # 格式化输出各项信息
        print(f"股票代码: {row['symbol']}")
        print(f"股票名称: {row['name']}")
        print(f"最新价格: {row['price']:.2f} 元")
        print(f"所属行业: {row['industry']}")
        print(f"上市日期: {row['listing_date'].strftime('%Y年%m月%d日')}")

        print("\n股本信息：")
        print(f"  总股本: {row['total_shares'] / 1e8:.2f} 亿股")
        print(f"  流通股: {row['float_shares'] / 1e8:.2f} 亿股")
        print(f"  流通比例: {row['float_shares'] / row['total_shares'] * 100:.2f}%")

        print("\n市值信息：")
        print(f"  总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
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
