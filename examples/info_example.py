#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票基本信息示例程序

本示例展示如何使用 akshare-one 的股票基本信息模块获取和分析数据。

依赖：
- pandas

运行方式：
    python info_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#info
"""

import pandas as pd

from akshare_one import get_basic_info
from akshare_one.modules.info import InfoDataFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_single_stock_info():
    """场景 1：查询单个股票基本信息"""
    print("\n" + "=" * 80)
    print("场景 1：查询单个股票基本信息")
    print("=" * 80)

    try:
        symbol = "600000"

        print(f"\n查询股票：{symbol}（浦发银行）")

        df = get_basic_info(symbol=symbol)

        if df.empty:
            print("无基本信息返回")
            return

        print("\n浦发银行(600000)基本信息：")
        print(df.to_string(index=False))

        row = df.iloc[0]
        print("\n关键信息摘要：")
        print(f"  股票名称: {row['name']}")
        print(f"  最新价格: {row['price']:.2f} 元")
        print(f"  所属行业: {row['industry']}")
        print(f"  总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
        print(f"  流通市值: {row['float_market_cap'] / 1e8:.2f} 亿元")
        print(f"  上市日期: {row['listing_date']}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票代码可能不存在或已退市")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_batch_stocks_info():
    """场景 2：批量查询多只股票信息"""
    print("\n" + "=" * 80)
    print("场景 2：批量查询多只股票信息")
    print("=" * 80)

    symbols = ["600000", "000001", "600519", "000858", "600036"]

    print(f"\n查询股票列表：{symbols}")

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

        print(f"\n成功获取 {len(df_all)} 只股票的信息：")
        display_cols = ["symbol", "name", "price", "industry", "total_market_cap"]
        available_cols = [col for col in display_cols if col in df_all.columns]
        print(df_all[available_cols].to_string(index=False))

        print("\n行业分布：")
        industry_counts = df_all["industry"].value_counts()
        for industry, count in industry_counts.items():
            print(f"  {industry}: {count} 只")


def scenario_3_industry_comparison():
    """场景 3：行业对比分析"""
    print("\n" + "=" * 80)
    print("场景 3：行业对比分析")
    print("=" * 80)

    stocks_by_industry = {
        "银行": ["600000", "601398", "601288"],
        "白酒": ["600519", "000858", "000568"],
        "新能源": ["002594", "300750", "600438"],
    }

    print("\n各行业代表股票信息：")

    all_results = []
    for industry, symbols in stocks_by_industry.items():
        print(f"\n【{industry}】行业：")

        for symbol in symbols:
            try:
                df = get_basic_info(symbol=symbol)
                if not df.empty:
                    row = df.iloc[0]
                    print(f"  {row['name']}({symbol}):")
                    print(f"    最新价: {row['price']:.2f} 元")
                    if "total_market_cap" in row:
                        print(f"    总市值: {row['total_market_cap'] / 1e8:.2f} 亿元")
                    all_results.append(df)
            except Exception as e:
                print(f"  {symbol}: 获取失败 ({e})")

    if len(all_results) > 1:
        df_merged = pd.concat(all_results, ignore_index=True)
        print("\n行业市值对比：")
        if "industry" in df_merged.columns and "total_market_cap" in df_merged.columns:
            industry_cap = df_merged.groupby("industry")["total_market_cap"].sum().sort_values(ascending=False)
            for ind, cap in industry_cap.items():
                print(f"  {ind}: {cap / 1e8:.2f} 亿元")


def scenario_4_multi_source():
    """场景 4：使用多数据源获取信息"""
    print("\n" + "=" * 80)
    print("场景 4：使用多数据源获取信息")
    print("=" * 80)

    try:
        available_sources = InfoDataFactory.get_available_sources()
        print(f"\n可用的数据源：{available_sources}")

        symbol = "600000"
        print(f"\n查询股票：{symbol}")

        for source in available_sources:
            try:
                df = get_basic_info(symbol=symbol, source=source)
                if not df.empty:
                    print(f"\n{source} 数据源返回：")
                    print(f"  股票名称: {df.iloc[0]['name']}")
                    print(f"  最新价格: {df.iloc[0]['price']:.2f} 元")
            except Exception as e:
                print(f"\n{source} 数据源失败: {e}")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("股票基本信息示例程序")
    print("=" * 80)

    scenario_1_single_stock_info()
    scenario_2_batch_stocks_info()
    scenario_3_industry_comparison()
    scenario_4_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
