#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期数据示例程序

本示例展示如何使用 akshare-one 的日期模块处理交易日期和日期转换。

依赖：
- pandas

运行方式：
    python date_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#date
"""

from datetime import datetime, timedelta, date

from akshare_one.modules.date import (
    get_all_trade_days,
    transform_date,
    get_trade_dates_between,
    is_trade_date,
)
from akshare_one.jq_compat.date import (
    get_shifted_date,
    get_previous_trade_date,
    get_next_trade_date,
    count_trade_dates_between,
    clear_trade_days_cache,
)


def scenario_1_get_all_trade_days():
    """场景 1：获取所有交易日期"""
    print("\n" + "=" * 80)
    print("场景 1：获取所有交易日期")
    print("=" * 80)

    try:
        print("\n获取所有交易日期...")

        trade_days = get_all_trade_days()

        if not trade_days:
            print("无交易日期数据返回")
            print("提示：数据源可能暂时无法访问")
            return

        print(f"\n总交易天数：{len(trade_days)}")
        print(f"\n最近10个交易日：")
        for d in trade_days[-10:]:
            print(f"  {d}")

        print(f"\n最早交易日：{trade_days[0]}")
        print(f"最新交易日：{trade_days[-1]}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_transform_date():
    """场景 2：日期格式转换"""
    print("\n" + "=" * 80)
    print("场景 2：日期格式转换")
    print("=" * 80)

    try:
        test_dates = [
            "2024-01-15",
            "20240115",
            "2024/01/15",
            datetime(2024, 1, 15),
            date(2024, 1, 15),
        ]

        print("\n测试不同格式的日期转换：")
        for d in test_dates:
            print(f"\n输入：{d} (类型：{type(d).__name__})")
            date_result = transform_date(d, "date")
            str_result = transform_date(d, "str")
            dt_result = transform_date(d, "datetime")
            ts_result = transform_date(d, "timestamp")
            print(f"  date: {date_result}")
            print(f"  str: {str_result}")
            print(f"  datetime: {dt_result}")
            print(f"  timestamp: {ts_result}")

    except ValueError as e:
        print(f"日期格式错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_get_trade_dates_between():
    """场景 3：获取日期区间的交易日"""
    print("\n" + "=" * 80)
    print("场景 3：获取日期区间的交易日")
    print("=" * 80)

    try:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n查询区间：{start_date} 至 {end_date}")

        trade_dates = get_trade_dates_between(start_date, end_date)

        if not trade_dates:
            print("该区间内无交易日")
            return

        print(f"\n区间内交易日数量：{len(trade_dates)}")
        print(f"\n区间内的交易日：")
        for d in trade_dates:
            print(f"  {d}")

        count = count_trade_dates_between(start_date, end_date)
        print(f"\n直接统计的交易日数量：{count}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_is_trade_date():
    """场景 4：判断是否为交易日"""
    print("\n" + "=" * 80)
    print("场景 4：判断是否为交易日")
    print("=" * 80)

    try:
        test_dates = [
            datetime.now(),
            datetime.now() - timedelta(days=2),
            "2024-01-01",
            "2024-01-06",
            "2024-05-01",
        ]

        print("\n测试日期是否为交易日：")
        for d in test_dates:
            result = is_trade_date(d)
            status = "是交易日" if result else "非交易日"
            print(f"  {d} -> {status}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_5_shift_trade_date():
    """场景 5：日期偏移（交易日）"""
    print("\n" + "=" * 80)
    print("场景 5：日期偏移（交易日）")
    print("=" * 80)

    try:
        base_date = datetime.now().strftime("%Y-%m-%d")
        print(f"\n基准日期：{base_date}")

        prev_1 = get_previous_trade_date(base_date, 1)
        prev_5 = get_previous_trade_date(base_date, 5)
        next_1 = get_next_trade_date(base_date, 1)
        next_5 = get_next_trade_date(base_date, 5)

        print(f"\n前1个交易日：{prev_1}")
        print(f"前5个交易日：{prev_5}")
        print(f"后1个交易日：{next_1}")
        print(f"后5个交易日：{next_5}")

        print("\n使用 get_shifted_date：")
        shifted = get_shifted_date(base_date, 10, "T")
        print(f"向后偏移10个交易日：{shifted}")

        shifted_back = get_shifted_date(shifted, -10, "T")
        print(f"向前偏移10个交易日：{shifted_back}")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_6_cache_management():
    """场景 6：缓存管理"""
    print("\n" + "=" * 80)
    print("场景 6：缓存管理")
    print("=" * 80)

    try:
        print("\n首次获取交易日期（可能从网络加载）：")
        trade_days_1 = get_all_trade_days()
        print(f"  缓存后数量：{len(trade_days_1)}")

        print("\n再次获取（使用缓存）：")
        trade_days_2 = get_all_trade_days()
        print(f"  缓存后数量：{len(trade_days_2)}")

        print("\n清除缓存：")
        clear_trade_days_cache()
        print("  缓存已清除")

        print("\n清除后获取（重新从网络加载）：")
        trade_days_3 = get_all_trade_days()
        print(f"  重新加载后数量：{len(trade_days_3)}")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("日期数据示例程序")
    print("=" * 80)

    scenario_1_get_all_trade_days()

    scenario_2_transform_date()

    scenario_3_get_trade_dates_between()

    scenario_4_is_trade_date()

    scenario_5_shift_trade_date()

    scenario_6_cache_management()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
