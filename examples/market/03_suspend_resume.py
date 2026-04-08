#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
停复牌数据示例程序

本示例展示如何使用 akshare-one 的停复牌模块获取和分析数据。

依赖：
- pandas

运行方式：
    python 03_suspend_resume.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#suspended
"""

from datetime import datetime, timedelta
import pandas as pd

# 导入模块
from akshare_one.modules.suspended import get_suspended_stocks
from akshare_one.modules.suspended import SuspendedFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_current_suspended_stocks():
    """场景 1：查询当日停牌股票"""
    print("\n" + "=" * 80)
    print("场景 1：查询当日停牌股票")
    print("=" * 80)

    try:
        print("\n正在获取当前停牌股票...")

        # 接口调用：获取停牌股票数据
        df = get_suspended_stocks()

        # 数据处理
        if df.empty:
            print("当前无停牌股票")
            return

        # 将日期列转换为 datetime 类型
        df["suspend_date"] = pd.to_datetime(df["suspend_date"])
        df["expected_resume_date"] = pd.to_datetime(df["expected_resume_date"])

        # 获取今天的日期
        today = datetime.now().date()

        # 筛选当日停牌的股票
        today_suspended = df[df["suspend_date"].dt.date == today]

        # 结果展示
        print(f"\n当前停牌股票（共 {len(df)} 只）：")
        print(
            df[["symbol", "name", "suspend_date", "expected_resume_date", "suspend_reason_type"]]
            .head(20)
            .to_string(index=False)
        )

        if not today_suspended.empty:
            print(f"\n今日新增停牌股票（{len(today_suspended)} 只）：")
            print(today_suspended[["symbol", "name", "suspend_reason_type"]].to_string(index=False))

        # 统计分析
        print("\n停牌股票统计：")
        print(f"停牌股票总数：{len(df)} 只")

        # 按市场统计
        market_stats = df.groupby("market").size() if "market" in df.columns else None
        if market_stats is not None:
            print("\n按市场统计：")
            for market, count in market_stats.items():
                print(f"  {market}: {count} 只")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有停牌股票或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_resumed_stocks():
    """场景 2：查询当日复牌股票"""
    print("\n" + "=" * 80)
    print("场景 2：查询当日复牌股票")
    print("=" * 80)

    try:
        print("\n正在获取停牌股票数据...")

        # 接口调用：获取停牌股票数据
        df = get_suspended_stocks()

        # 数据处理
        if df.empty:
            print("无停牌股票数据")
            return

        # 将日期列转换为 datetime 类型
        df["suspend_date"] = pd.to_datetime(df["suspend_date"])
        df["expected_resume_date"] = pd.to_datetime(df["expected_resume_date"])
        if "suspend_end_date" in df.columns:
            df["suspend_end_date"] = pd.to_datetime(df["suspend_end_date"])

        # 获取今天的日期
        today = datetime.now().date()

        # 筛选预计今日复牌的股票
        today_resume = df[df["expected_resume_date"].dt.date == today]

        # 结果展示
        if today_resume.empty:
            print(f"今日（{today}）无预计复牌的股票")
        else:
            print(f"\n今日预计复牌股票（共 {len(today_resume)} 只）：")
            print(today_resume[["symbol", "name", "suspend_date", "suspend_reason_type"]].to_string(index=False))

        # 查找即将复牌的股票（未来3天内）
        future_3days = (datetime.now() + timedelta(days=3)).date()
        upcoming_resume = df[
            (df["expected_resume_date"].dt.date >= today) & (df["expected_resume_date"].dt.date <= future_3days)
        ]

        if not upcoming_resume.empty:
            print(f"\n未来3天内预计复牌的股票（共 {len(upcoming_resume)} 只）：")
            print(
                upcoming_resume[
                    ["symbol", "name", "expected_resume_date", "suspend_date", "suspend_reason_type"]
                ].to_string(index=False)
            )

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有停牌股票或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_historical_suspensions():
    """场景 3：查询历史停牌记录"""
    print("\n" + "=" * 80)
    print("场景 3：查询历史停牌记录")
    print("=" * 80)

    try:
        print("\n正在获取停牌股票数据...")

        # 接口调用：获取停牌股票数据
        df = get_suspended_stocks()

        # 数据处理
        if df.empty:
            print("无停牌股票数据")
            return

        # 按停牌日期排序
        df_sorted = df.sort_values("suspend_date", ascending=False)

        # 结果展示：显示最近的停牌记录
        print("\n最近的停牌记录（按停牌日期降序）：")
        print(
            df_sorted[["symbol", "name", "suspend_date", "expected_resume_date", "suspend_reason_type"]]
            .head(30)
            .to_string(index=False)
        )

        # 统计分析：按停牌期限分类
        if "suspend_duration_type" in df.columns:
            duration_stats = df["suspend_duration_type"].value_counts()
            print("\n停牌期限分布：")
            for duration, count in duration_stats.items():
                print(f"  {duration}: {count} 只")

        # 找出停牌时间最长的股票（无预计复牌时间的）
        no_resume_date = df[df["expected_resume_date"].isna()]
        if not no_resume_date.empty:
            print(f"\n长期停牌股票（无预计复牌时间，共 {len(no_resume_date)} 只）：")
            print(no_resume_date[["symbol", "name", "suspend_date", "suspend_reason_type"]].to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有停牌股票或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_4_suspend_reason_type_statistics():
    """场景 4：停牌原因统计"""
    print("\n" + "=" * 80)
    print("场景 4：停牌原因统计")
    print("=" * 80)

    try:
        print("\n正在获取停牌股票数据...")

        # 接口调用：获取停牌股票数据
        df = get_suspended_stocks()

        # 数据处理
        if df.empty:
            print("无停牌股票数据")
            return

        # 将日期列转换为 datetime 类型
        df["suspend_date"] = pd.to_datetime(df["suspend_date"])
        df["expected_resume_date"] = pd.to_datetime(df["expected_resume_date"])

        # 统计分析：按停牌原因分类
        suspend_reason_type_stats = df["suspend_reason_type"].value_counts()

        print("\n停牌原因统计：")
        print(f"{'停牌原因':<30} {'数量':>10} {'占比':>10}")
        print("-" * 52)
        for suspend_reason_type, count in suspend_reason_type_stats.items():
            percentage = (count / len(df)) * 100
            print(f"{suspend_reason_type:<30} {count:>10} {percentage:>9.2f}%")
        print("-" * 52)
        print(f"{'总计':<30} {len(df):>10} {'100.00%':>10}")

        # 找出主要停牌原因（占比超过10%的）
        major_suspend_reason_types = suspend_reason_type_stats[suspend_reason_type_stats / len(df) > 0.1]
        if not major_suspend_reason_types.empty:
            print("\n主要停牌原因（占比超过10%）：")
            for suspend_reason_type, count in major_suspend_reason_types.items():
                percentage = (count / len(df)) * 100
                print(f"  {suspend_reason_type}: {count} 只（{percentage:.2f}%）")

        # 按停牌原因分组，统计平均停牌时长
        if "expected_resume_date" in df.columns and "suspend_date" in df.columns:
            print("\n各停牌原因的平均停牌天数：")
            df_valid = df.dropna(subset=["expected_resume_date"])
            if not df_valid.empty:
                df_valid["suspend_duration_type_days"] = (
                    df_valid["expected_resume_date"] - df_valid["suspend_date"]
                ).dt.days

                avg_duration_by_suspend_reason_type = (
                    df_valid.groupby("suspend_reason_type")["suspend_duration_type_days"]
                    .mean()
                    .sort_values(ascending=False)
                )

                for suspend_reason_type, avg_days in avg_duration_by_suspend_reason_type.items():
                    if avg_days > 0:
                        print(f"  {suspend_reason_type}: {avg_days:.1f} 天")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有停牌股票或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_5_duration_analysis():
    """场景 5：停牌时长分析"""
    print("\n" + "=" * 80)
    print("场景 5：停牌时长分析")
    print("=" * 80)

    try:
        print("\n正在获取停牌股票数据...")

        # 接口调用：获取停牌股票数据
        df = get_suspended_stocks()

        # 数据处理
        if df.empty:
            print("无停牌股票数据")
            return

        # 将日期列转换为 datetime 类型
        df["suspend_date"] = pd.to_datetime(df["suspend_date"])
        df["expected_resume_date"] = pd.to_datetime(df["expected_resume_date"])

        # 计算停牌时长（对于有预计复牌时间的股票）
        df_valid = df.dropna(subset=["expected_resume_date"]).copy()

        if df_valid.empty:
            print("无有效的停牌时长数据")
            return

        # 计算停牌天数
        df_valid["suspend_days"] = (df_valid["expected_resume_date"] - df_valid["suspend_date"]).dt.days

        # 结果展示
        print("\n停牌时长分析：")
        print(f"有明确复牌时间的股票：{len(df_valid)} 只")
        print(f"无明确复牌时间的股票：{len(df) - len(df_valid)} 只")

        # 统计分析
        if not df_valid.empty:
            avg_days = df_valid["suspend_days"].mean()
            max_days = df_valid["suspend_days"].max()
            min_days = df_valid["suspend_days"].min()
            median_days = df_valid["suspend_days"].median()

            print(f"\n停牌时长统计：")
            print(f"  平均停牌天数：{avg_days:.1f} 天")
            print(f"  最长停牌天数：{max_days} 天")
            print(f"  最短停牌天数：{min_days} 天")
            print(f"  中位数停牌天数：{median_days:.1f} 天")

            # 停牌时长分布
            print("\n停牌时长分布：")
            duration_bins = [0, 1, 3, 7, 15, 30, 60, 90, float("inf")]
            duration_labels = ["1天", "2-3天", "4-7天", "8-15天", "16-30天", "31-60天", "61-90天", "90天以上"]

            df_valid["duration_group"] = pd.cut(
                df_valid["suspend_days"], bins=duration_bins, labels=duration_labels, right=True
            )

            duration_distribution = df_valid["duration_group"].value_counts().sort_index()
            for duration, count in duration_distribution.items():
                if count > 0:
                    percentage = (count / len(df_valid)) * 100
                    print(f"  {duration}: {count} 只（{percentage:.2f}%）")

            # 停牌时间最长的股票
            longest_suspended = df_valid.nlargest(10, "suspend_days")
            print("\n停牌时间最长的10只股票：")
            print(
                longest_suspended[
                    ["symbol", "name", "suspend_date", "expected_resume_date", "suspend_days", "suspend_reason_type"]
                ].to_string(index=False)
            )

            # 停牌时间最短的股票
            shortest_suspended = df_valid.nsmallest(10, "suspend_days")
            print("\n停牌时间最短的10只股票：")
            print(
                shortest_suspended[
                    ["symbol", "name", "suspend_date", "expected_resume_date", "suspend_days", "suspend_reason_type"]
                ].to_string(index=False)
            )

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有停牌股票或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("停复牌数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_current_suspended_stocks()
    scenario_2_resumed_stocks()
    scenario_3_historical_suspensions()
    scenario_4_suspend_reason_type_statistics()
    scenario_5_duration_analysis()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
