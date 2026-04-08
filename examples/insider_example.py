#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内部交易数据示例程序

本示例展示如何使用 akshare-one 的内部交易模块获取和分析数据。

依赖：
- pandas

运行方式：
    python insider_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#insider
"""

import pandas as pd

from akshare_one import get_inner_trade_data
from akshare_one.modules.insider import InsiderDataFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_single_stock_insider_trades():
    """场景 1：查询单只股票内部交易记录"""
    print("\n" + "=" * 80)
    print("场景 1：查询单只股票内部交易记录")
    print("=" * 80)

    try:
        symbol = "600000"

        print(f"\n查询股票：{symbol}（浦发银行）")

        df = get_inner_trade_data(symbol=symbol)

        if df.empty:
            print("无内部交易数据返回")
            print("提示：该股票可能没有内部交易记录或数据尚未更新")
            return

        print(f"\n获取到 {len(df)} 条内部交易记录")
        print("\n内部交易记录：")
        print(df.to_string(index=False))

        if "change_amount" in df.columns:
            total_change = df["change_amount"].sum()
            print(f"\n累计变动金额：{total_change:,.2f} 元")

        if "insider_name" in df.columns:
            insider_counts = df["insider_name"].value_counts()
            print("\n主要交易人员：")
            for name, count in insider_counts.head(5).items():
                print(f"  {name}: {count} 次")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有内部交易记录")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_analyze_trend():
    """场景 2：分析内部交易趋势"""
    print("\n" + "=" * 80)
    print("场景 2：分析内部交易趋势")
    print("=" * 80)

    try:
        symbols = ["600519", "000858", "600036"]

        print(f"\n查询股票列表：{symbols}")

        all_results = []
        for symbol in symbols:
            try:
                df = get_inner_trade_data(symbol=symbol)
                if not df.empty:
                    df["symbol"] = symbol
                    all_results.append(df)
                    print(f"  {symbol}: 获取到 {len(df)} 条记录")
            except Exception as e:
                print(f"  {symbol}: 获取失败 ({e})")

        if all_results:
            df_merged = pd.concat(all_results, ignore_index=True)

            print(f"\n累计获取 {len(df_merged)} 条内部交易记录")

            if "change_amount" in df_merged.columns:
                print("\n按股票统计变动金额：")
                stock_stats = df_merged.groupby("symbol")["change_amount"].agg(["sum", "mean", "count"])
                print(stock_stats.to_string())

            if "transaction_type" in df_merged.columns or "change_type" in df_merged.columns:
                col = "transaction_type" if "transaction_type" in df_merged.columns else "change_type"
                print("\n交易类型分布：")
                type_counts = df_merged[col].value_counts()
                for t, count in type_counts.items():
                    print(f"  {t}: {count} 次")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_multi_source():
    """场景 3：使用多数据源获取内部交易数据"""
    print("\n" + "=" * 80)
    print("场景 3：使用多数据源获取内部交易数据")
    print("=" * 80)

    try:
        available_sources = InsiderDataFactory.get_available_sources()
        print(f"\n可用的数据源：{available_sources}")

        symbol = "600519"
        print(f"\n查询股票：{symbol}（贵州茅台）")

        for source in available_sources:
            try:
                df = get_inner_trade_data(symbol=symbol, source=source)
                if not df.empty:
                    print(f"\n{source} 数据源返回：")
                    print(f"  记录数: {len(df)}")
                    if "change_amount" in df.columns:
                        print(f"  累计变动: {df['change_amount'].sum():,.2f} 元")
                else:
                    print(f"\n{source} 数据源: 无数据返回")
            except Exception as e:
                print(f"\n{source} 数据源失败: {e}")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("内部交易数据示例程序")
    print("=" * 80)

    scenario_1_single_stock_insider_trades()
    scenario_2_analyze_trend()
    scenario_3_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
