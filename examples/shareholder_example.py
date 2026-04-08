#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股东数据示例程序

本示例展示如何使用 akshare-one 的股东模块获取和分析数据。

依赖：
- pandas

运行方式：
    python shareholder_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#shareholder
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.shareholder import (
    get_shareholder_changes,
    get_top_shareholders,
    get_institution_holdings,
)
from akshare_one.modules.shareholder import ShareholderFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_shareholder_changes():
    """场景 1：查询股东增减持变化"""
    print("\n" + "=" * 80)
    print("场景 1：查询股东增减持变化")
    print("=" * 80)

    try:
        symbol = "600000"
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")
        print(f"时间范围：{start_date} 至 {end_date}")

        df = get_shareholder_changes(symbol, start_date, end_date)

        if df.empty:
            print("无股东增减持数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n最近10条股东增减持记录：")
        print(df.head(10).to_string(index=False))

        total_change = 0
        if "change_shares" in df.columns:
            total_change = df["change_shares"].sum()
            print(f"\n总增减持股份：{total_change:,.0f} 股")

        increase_count = 0
        decrease_count = 0
        if "change_ratio" in df.columns:
            increase_count = len(df[df["change_ratio"] > 0])
            decrease_count = len(df[df["change_ratio"] < 0])
            print(f"增持次数：{increase_count}")
            print(f"减持次数：{decrease_count}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能在此期间没有增减持记录")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_top_shareholders():
    """场景 2：查询十大股东数据"""
    print("\n" + "=" * 80)
    print("场景 2：查询十大股东数据")
    print("=" * 80)

    try:
        symbol = "600000"

        print(f"\n查询股票：{symbol}")

        df = get_top_shareholders(symbol)

        if df.empty:
            print("无十大股东数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n十大股东列表：")
        print(df.to_string(index=False))

        if "hold_ratio" in df.columns:
            total_hold_ratio = df["hold_ratio"].sum()
            print(f"\n前十大股东合计持股比例：{total_hold_ratio:.2f}%")

        if "shareholder_type" in df.columns:
            inst_count = len(df[df["shareholder_type"] == "机构"])
            print(f"机构股东数量：{inst_count}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有十大股东数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_institution_holdings():
    """场景 3：查询机构持股数据"""
    print("\n" + "=" * 80)
    print("场景 3：查询机构持股数据")
    print("=" * 80)

    try:
        symbol = "600000"

        print(f"\n查询股票：{symbol}")

        df = get_institution_holdings(symbol)

        if df.empty:
            print("无机构持股数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n机构持股数据：")
        print(df.to_string(index=False))

        if "hold_amount" in df.columns:
            total_hold = df["hold_amount"].sum()
            print(f"\n机构合计持股数量：{total_hold:,.0f}")

        if "inst_type" in df.columns:
            inst_types = df["inst_type"].value_counts()
            print("\n机构类型分布：")
            for inst_type, count in inst_types.items():
                print(f"  {inst_type}: {count} 家")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有机构持股数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_multi_source():
    """场景 4：使用备用数据源"""
    print("\n" + "=" * 80)
    print("场景 4：使用备用数据源")
    print("=" * 80)

    try:
        available_sources = ShareholderFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        if "eastmoney" in available_sources:
            em_provider = ShareholderFactory.get_provider("eastmoney")
            print(f"\n使用 eastmoney 数据源")
            print(f"  提供商类型：{type(em_provider).__name__}")
            print(f"  数据源名称：{em_provider.get_source_name()}")

            symbol = "600000"
            df = em_provider.get_top_shareholders(symbol)
            if df.empty:
                print("无数据返回")
            else:
                print(f"\n获取到 {len(df)} 条记录")
                print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("股东数据示例程序")
    print("=" * 80)

    scenario_1_shareholder_changes()
    scenario_2_top_shareholders()
    scenario_3_institution_holdings()
    scenario_4_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
