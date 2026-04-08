#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业绩数据示例程序

本示例展示如何使用 akshare-one 的业绩模块获取和分析上市公司业绩数据。

依赖：
- pandas

运行方式：
    python performance_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#performance
"""

from akshare_one.modules.performance import (
    get_performance_forecast,
    get_performance_express,
)
from akshare_one.modules.performance import PerformanceFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_performance_forecast():
    """场景 1：获取业绩预告数据"""
    print("\n" + "=" * 80)
    print("场景 1：获取业绩预告数据")
    print("=" * 80)

    try:
        date = "20240930"
        print(f"\n查询日期：{date}（2024年三季报）")

        df = get_performance_forecast(date)

        if df.empty:
            print("无业绩预告数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n业绩预告数据（前10条）：")
        display_columns = ["symbol", "name", "report_date", "forecast_type", "net_profit"]
        available_columns = [col for col in display_columns if col in df.columns]
        if available_columns:
            print(df.head(10)[available_columns].to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

        if "forecast_type" in df.columns:
            type_counts = df["forecast_type"].value_counts()
            print("\n业绩预告类型统计：")
            for ftype, count in type_counts.head(5).items():
                print(f"  {ftype}: {count} 家")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYYMMDD，如 '20240930'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该报告期可能没有业绩预告数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_get_performance_express():
    """场景 2：获取业绩快报数据"""
    print("\n" + "=" * 80)
    print("场景 2：获取业绩快报数据")
    print("=" * 80)

    try:
        date = "20240930"
        print(f"\n查询日期：{date}（2024年三季报）")

        df = get_performance_express(date)

        if df.empty:
            print("无业绩快报数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n业绩快报数据（前10条）：")
        display_columns = ["symbol", "name", "report_date", "营业收入", "净利润"]
        available_columns = [col for col in display_columns if col in df.columns]
        if available_columns:
            print(df.head(10)[available_columns].to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

        if "净利润" in df.columns:
            try:
                df_sorted = df.sort_values("净利润", ascending=False)
                print("\n净利润排名前5：")
                print(df_sorted.head(5)[["symbol", "name", "净利润"]].to_string(index=False))
            except Exception:
                pass

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYYMMDD，如 '20240930'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该报告期可能没有业绩快报数据")
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
        available_sources = PerformanceFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        date = "20240930"

        for source in available_sources:
            print(f"\n使用 {source} 数据源：")
            provider = PerformanceFactory.get_provider(source)
            print(f"  提供商类型：{type(provider).__name__}")
            print(f"  数据源名称：{provider.get_source_name()}")

            try:
                df = get_performance_express(date, source=source)
                if df.empty:
                    print("  无数据返回")
                else:
                    print(f"  获取到 {len(df)} 条记录")
            except Exception as e:
                print(f"  获取数据失败：{e}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_compare_quarters():
    """场景 4：对比不同季度业绩"""
    print("\n" + "=" * 80)
    print("场景 4：对比不同季度业绩")
    print("=" * 80)

    try:
        dates = ["20240630", "20240930"]
        print(f"\n查询季度：{dates}")

        all_data = {}
        for date in dates:
            df = get_performance_express(date)
            if not df.empty:
                all_data[date] = df
                print(f"\n{date} 财报：获取到 {len(df)} 条记录")

        if len(all_data) >= 2:
            latest_date = dates[-1]
            df_latest = all_data[latest_date]

            if "净利润" in df_latest.columns:
                df_sorted = df_latest.sort_values("净利润", ascending=False)
                print(f"\n{latest_date} 净利润前10：")
                print(df_sorted.head(10)[["symbol", "name", "净利润"]].to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("业绩数据示例程序")
    print("=" * 80)

    scenario_1_get_performance_forecast()
    scenario_2_get_performance_express()
    scenario_3_multi_source()
    scenario_4_compare_quarters()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
