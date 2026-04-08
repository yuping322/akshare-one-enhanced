#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块数据示例程序

本示例展示如何使用 akshare-one 的板块模块获取科创板和创业板股票数据。

依赖：
- pandas

运行方式：
    python board_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#board
"""

from datetime import datetime, timedelta

from akshare_one.modules.board import get_kcb_stocks, get_cyb_stocks
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_kcb_stocks():
    """场景 1：获取科创板股票列表"""
    print("\n" + "=" * 80)
    print("场景 1：获取科创板（KCB）股票列表")
    print("=" * 80)

    try:
        print("\n获取科创板股票数据...")

        df = get_kcb_stocks()

        if df.empty:
            print("无科创板股票数据返回")
            print("提示：该板块可能暂时没有数据，请稍后重试")
            return

        print(f"\n获取到 {len(df)} 只科创板股票")
        print("\n前10只科创板股票：")
        print(df.head(10).to_string(index=False))

        if "pct_change" in df.columns or "change_rate" in df.columns:
            pct_col = "pct_change" if "pct_change" in df.columns else "change_rate"
            df_sorted = df.sort_values(pct_col, ascending=False)
            print(f"\n涨幅最大的前10只科创板股票（按{pct_col}排序）：")
            print(df_sorted.head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该板块可能暂时没有数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_get_cyb_stocks():
    """场景 2：获取创业板股票列表"""
    print("\n" + "=" * 80)
    print("场景 2：获取创业板（CYB）股票列表")
    print("=" * 80)

    try:
        print("\n获取创业板股票数据...")

        df = get_cyb_stocks()

        if df.empty:
            print("无创业板股票数据返回")
            print("提示：该板块可能暂时没有数据，请稍后重试")
            return

        print(f"\n获取到 {len(df)} 只创业板股票")
        print("\n前10只创业板股票：")
        print(df.head(10).to_string(index=False))

        if "pct_change" in df.columns or "change_rate" in df.columns:
            pct_col = "pct_change" if "pct_change" in df.columns else "change_rate"
            df_sorted = df.sort_values(pct_col, ascending=False)
            print(f"\n涨幅最大的前10只创业板股票（按{pct_col}排序）：")
            print(df_sorted.head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该板块可能暂时没有数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_compare_boards():
    """场景 3：对比科创板和创业板"""
    print("\n" + "=" * 80)
    print("场景 3：对比科创板和创业板")
    print("=" * 80)

    try:
        kcb_df = get_kcb_stocks()
        cyb_df = get_cyb_stocks()

        if kcb_df.empty and cyb_df.empty:
            print("无板块数据返回")
            return

        print(f"\n科创板股票数量：{len(kcb_df)}")
        print(f"创业板股票数量：{len(cyb_df)}")

        if not kcb_df.empty:
            pct_col = "pct_change" if "pct_change" in kcb_df.columns else "change_rate"
            if pct_col in kcb_df.columns:
                kcb_avg_change = kcb_df[pct_col].mean()
                kcb_max_change = kcb_df[pct_col].max()
                kcb_min_change = kcb_df[pct_col].min()
                print(f"\n科创板涨跌幅统计：")
                print(f"  平均涨跌幅：{kcb_avg_change:.2f}%")
                print(f"  最大涨幅：{kcb_max_change:.2f}%")
                print(f"  最大跌幅：{kcb_min_change:.2f}%")

        if not cyb_df.empty:
            pct_col = "pct_change" if "pct_change" in cyb_df.columns else "change_rate"
            if pct_col in cyb_df.columns:
                cyb_avg_change = cyb_df[pct_col].mean()
                cyb_max_change = cyb_df[pct_col].max()
                cyb_min_change = cyb_df[pct_col].min()
                print(f"\n创业板涨跌幅统计：")
                print(f"  平均涨跌幅：{cyb_avg_change:.2f}%")
                print(f"  最大涨幅：{cyb_max_change:.2f}%")
                print(f"  最大跌幅：{cyb_min_change:.2f}%")

        if not kcb_df.empty and not cyb_df.empty:
            total = len(kcb_df) + len(cyb_df)
            print(f"\n两个板块合计：{total} 只股票")

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
    print("板块数据示例程序")
    print("=" * 80)

    scenario_1_get_kcb_stocks()

    scenario_2_get_cyb_stocks()

    scenario_3_compare_boards()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
