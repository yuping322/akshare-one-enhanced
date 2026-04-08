#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 6：导出数据到CSV

本示例展示如何将 akshare-one 获取的数据导出到文件，包括：
- 导出为CSV格式
- 导出为Excel格式
- 批量导出多个股票数据

运行方式：
    python examples/basic/06_export_to_csv.py
"""

import os
from datetime import datetime
import pandas as pd
from akshare_one import get_hist_data_multi_source, get_realtime_data_multi_source, get_basic_info


def example_export_to_csv():
    """示例1：导出为CSV格式"""
    print("\n" + "=" * 60)
    print("示例1：导出为CSV格式")
    print("=" * 60)

    # 获取历史数据
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["eastmoney_direct", "eastmoney", "sina"],
    )

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 导出为CSV
    filename = f"{output_dir}/600000_daily_2024.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n数据已导出到: {filename}")
    print(f"数据条数: {len(df)}")

    # 验证文件
    df_loaded = pd.read_csv(filename)
    print(f"验证: 成功加载 {len(df_loaded)} 条数据")


def example_export_to_excel():
    """示例2：导出为Excel格式"""
    print("\n" + "=" * 60)
    print("示例2：导出为Excel格式")
    print("=" * 60)

    # 获取历史数据
    df = get_hist_data_multi_source(
        symbol="000001",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["eastmoney_direct", "eastmoney", "sina"],
    )

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 导出为Excel（需要移除时区信息）
    filename = f"{output_dir}/000001_daily_2024.xlsx"
    df_excel = df.copy()
    if df_excel["timestamp"].dt.tz is not None:
        df_excel["timestamp"] = df_excel["timestamp"].dt.tz_convert(None)
    df_excel.to_excel(filename, index=False, engine="openpyxl")

    print(f"\n数据已导出到: {filename}")
    print(f"数据条数: {len(df)}")


def example_export_with_formatting():
    """示例3：导出并格式化"""
    print("\n" + "=" * 60)
    print("示例3：导出并格式化")
    print("=" * 60)

    # 获取实时行情
    df = get_realtime_data_multi_source(symbol="000001", sources=["eastmoney_direct", "xueqiu"])

    # 添加时间戳列
    df["export_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 排序：按涨跌幅降序
    df_sorted = df.sort_values("pct_change", ascending=False)

    # 重命名列（中文）
    df_formatted = df_sorted.rename(
        columns={
            "symbol": "股票代码",
            "price": "最新价",
            "change": "涨跌额",
            "pct_change": "涨跌幅(%)",
            "open": "今开",
            "high": "最高",
            "low": "最低",
            "prev_close": "昨收",
            "volume": "成交量(手)",
            "amount": "成交额(元)",
            "export_time": "导出时间",
        }
    )

    # 导出
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/market_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_formatted.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n市场概览已导出到: {filename}")
    print(f"股票数量: {len(df_formatted)}")


def example_export_multiple_stocks():
    """示例4：批量导出多个股票"""
    print("\n" + "=" * 60)
    print("示例4：批量导出多个股票")
    print("=" * 60)

    stocks = ["600000", "000001", "600519", "000858", "600036"]
    output_dir = "output/stocks"
    os.makedirs(output_dir, exist_ok=True)

    for symbol in stocks:
        print(f"\n处理股票: {symbol}")

        # 获取数据
        df = get_hist_data_multi_source(
            symbol=symbol,
            interval="day",
            start_date="2024-01-01",
            end_date="2024-12-31",
            sources=["eastmoney_direct", "eastmoney", "sina"],
        )

        # 导出
        filename = f"{output_dir}/{symbol}_2024.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        print(f"  已导出: {filename} ({len(df)} 条数据)")


def example_export_with_statistics():
    """示例5：导出带统计数据"""
    print("\n" + "=" * 60)
    print("示例5：导出带统计数据")
    print("=" * 60)

    # 获取数据
    df = get_hist_data_multi_source(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["eastmoney_direct", "eastmoney", "sina"],
    )

    # 计算统计指标
    df["pct_change"] = df["close"].pct_change() * 100
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma10"] = df["close"].rolling(window=10).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()

    # 创建统计摘要
    stats = pd.DataFrame(
        {
            "统计项": [
                "数据条数",
                "平均收盘价",
                "最高价",
                "最低价",
                "平均涨跌幅(%)",
                "最大涨幅(%)",
                "最大跌幅(%)",
                "平均成交量(手)",
            ],
            "值": [
                len(df),
                f"{df['close'].mean():.2f}",
                f"{df['high'].max():.2f}",
                f"{df['low'].min():.2f}",
                f"{df['pct_change'].mean():.2f}",
                f"{df['pct_change'].max():.2f}",
                f"{df['pct_change'].min():.2f}",
                f"{df['volume'].mean():.0f}",
            ],
        }
    )

    # 导出
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 导出数据
    data_file = f"{output_dir}/600000_with_indicators_2024.csv"
    df.to_csv(data_file, index=False, encoding="utf-8-sig")
    print(f"\n数据已导出到: {data_file}")

    # 导出统计摘要
    stats_file = f"{output_dir}/600000_statistics_2024.csv"
    stats.to_csv(stats_file, index=False, encoding="utf-8-sig")
    print(f"统计摘要已导出到: {stats_file}")

    print("\n统计摘要：")
    print(stats.to_string(index=False))


def example_export_to_multiple_formats():
    """示例6：同时导出多种格式"""
    print("\n" + "=" * 60)
    print("示例6：同时导出多种格式")
    print("=" * 60)

    # 获取数据
    df = get_hist_data_multi_source(
        symbol="600519",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31",
        sources=["eastmoney_direct", "eastmoney", "sina"],
    )

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    base_name = "600519_2024"

    # 导出CSV
    csv_file = f"{output_dir}/{base_name}.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"CSV: {csv_file}")

    # 导出Excel（需要移除时区信息）
    excel_file = f"{output_dir}/{base_name}.xlsx"
    df_excel = df.copy()
    if df_excel["timestamp"].dt.tz is not None:
        df_excel["timestamp"] = df_excel["timestamp"].dt.tz_convert(None)
    df_excel.to_excel(excel_file, index=False, engine="openpyxl")
    print(f"Excel: {excel_file}")

    # 导出JSON
    json_file = f"{output_dir}/{base_name}.json"
    df.to_json(json_file, orient="records", force_ascii=False, indent=2)
    print(f"JSON: {json_file}")

    print(f"\n已导出3种格式，数据条数: {len(df)}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 数据导出示例")
    print("=" * 60)

    # 运行所有示例
    example_export_to_csv()
    example_export_to_excel()
    example_export_with_formatting()
    example_export_multiple_stocks()
    example_export_with_statistics()
    example_export_to_multiple_formats()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
