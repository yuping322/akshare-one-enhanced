#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值数据示例程序

本示例展示如何使用 akshare-one 的估值模块获取和分析股票及市场估值数据。

依赖：
- pandas

运行方式：
    python valuation_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#valuation
"""

from datetime import datetime, timedelta

from akshare_one.modules.valuation import (
    get_stock_valuation,
    get_market_valuation,
)
from akshare_one.modules.valuation import ValuationFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_stock_valuation():
    """场景 1：获取个股估值数据"""
    print("\n" + "=" * 80)
    print("场景 1：获取个股估值数据")
    print("=" * 80)

    try:
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        df = get_stock_valuation(symbol, start_date, end_date)

        if df.empty:
            print("无估值数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n最近10条估值数据：")
        display_columns = ["date", "pe_ttm", "pb", "ps", "pcf"]
        available_columns = [col for col in display_columns if col in df.columns]
        if available_columns:
            print(df.head(10)[available_columns].to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

        if "pe_ttm" in df.columns:
            latest_pe = df["pe_ttm"].iloc[-1]
            avg_pe = df["pe_ttm"].mean()
            print(f"\nPE TTM 统计：")
            print(f"  最新值：{latest_pe:.2f}")
            print(f"  平均值：{avg_pe:.2f}")

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


def scenario_2_get_market_valuation():
    """场景 2：获取市场整体估值"""
    print("\n" + "=" * 80)
    print("场景 2：获取市场整体估值")
    print("=" * 80)

    try:
        print("\n查询全市场估值数据...")

        df = get_market_valuation()

        if df.empty:
            print("无市场估值数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n市场估值数据（前10条）：")
        display_columns = ["date", "market_pe", "market_pb", "turnover_rate"]
        available_columns = [col for col in display_columns if col in df.columns]
        if available_columns:
            print(df.head(10)[available_columns].to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

        if "market_pe" in df.columns:
            latest_pe = df["market_pe"].iloc[-1]
            avg_pe = df["market_pe"].mean()
            print(f"\n市场 PE TTM 统计：")
            print(f"  最新值：{latest_pe:.2f}")
            print(f"  历史平均值：{avg_pe:.2f}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_multi_source():
    """场景 3：使用不同数据源"""
    print("\n" + "=" * 80)
    print("场景 3：使用不同数据源")
    print("=" * 80)

    try:
        available_sources = ValuationFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        for source in available_sources:
            print(f"\n使用 {source} 数据源：")
            provider = ValuationFactory.get_provider(source)
            print(f"  提供商类型：{type(provider).__name__}")
            print(f"  数据源名称：{provider.get_source_name()}")

            try:
                df = get_market_valuation(source=source)
                if df.empty:
                    print("  无数据返回")
                else:
                    print(f"  获取到 {len(df)} 条记录")
            except Exception as e:
                print(f"  获取数据失败：{e}")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("估值数据示例程序")
    print("=" * 80)

    scenario_1_get_stock_valuation()
    scenario_2_get_market_valuation()
    scenario_3_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
