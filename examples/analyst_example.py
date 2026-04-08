#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析师数据示例程序

本示例展示如何使用 akshare-one 的分析师模块获取分析师排名和研究报告数据。

依赖：
- pandas

运行方式：
    python analyst_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#analyst
"""

from datetime import datetime, timedelta

from akshare_one.modules.analyst import get_analyst_rank, get_research_report
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_analyst_rank():
    """场景 1：获取分析师排名"""
    print("\n" + "=" * 80)
    print("场景 1：获取分析师排名")
    print("=" * 80)

    try:
        print("\n获取分析师排名数据...")

        df = get_analyst_rank()

        if df.empty:
            print("无分析师排名数据返回")
            return

        print(f"\n获取到 {len(df)} 条记录")
        print("\n前10名分析师：")
        print(df.head(10).to_string(index=False))

        if "rank" in df.columns:
            df_sorted = df.sort_values("rank")
            print("\n排名前10的分析师：")
            print(df_sorted.head(10).to_string(index=False))
        elif "total_rank" in df.columns:
            df_sorted = df.sort_values("total_rank")
            print("\n综合排名前10的分析师：")
            print(df_sorted.head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有分析师排名数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_get_research_report():
    """场景 2：获取研究报告"""
    print("\n" + "=" * 80)
    print("场景 2：获取个股研究报告")
    print("=" * 80)

    try:
        symbol = "000001"
        print(f"\n查询股票：{symbol}")

        df = get_research_report(symbol=symbol)

        if df.empty:
            print("无研究报告数据返回")
            print("提示：该股票可能没有研究报告或数据尚未更新")
            return

        print(f"\n获取到 {len(df)} 条研究报告")
        print("\n最近5条研究报告：")
        print(df.head(5).to_string(index=False))

        if "publish_date" in df.columns:
            df_sorted = df.sort_values("publish_date", ascending=False)
            print("\n最新发布的研究报告：")
            print(df_sorted.head(5).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '000001'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有研究报告")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_get_multiple_stocks_reports():
    """场景 3：获取多只股票的研究报告"""
    print("\n" + "=" * 80)
    print("场景 3：获取多只股票的研究报告")
    print("=" * 80)

    symbols = ["000001", "600519", "000002"]
    print(f"\n查询股票：{symbols}")

    for symbol in symbols:
        try:
            print(f"\n--- {symbol} ---")
            df = get_research_report(symbol=symbol)

            if df.empty:
                print("无研究报告")
                continue

            print(f"研究报告数量：{len(df)}")
            if "title" in df.columns:
                print("最新报告：")
                if "publish_date" in df.columns:
                    df_sorted = df.sort_values("publish_date", ascending=False)
                    print(df_sorted.head(3)[["title", "publish_date"]].to_string(index=False))
                else:
                    print(df.head(3)["title"].to_string(index=False))

        except InvalidParameterError as e:
            print(f"参数错误：{e}")
        except NoDataError as e:
            print(f"无数据：{e}")
        except DataSourceUnavailableError as e:
            print(f"数据源不可用：{e}")
        except Exception as e:
            print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("分析师数据示例程序")
    print("=" * 80)

    scenario_1_get_analyst_rank()

    scenario_2_get_research_report()

    scenario_3_get_multiple_stocks_reports()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
