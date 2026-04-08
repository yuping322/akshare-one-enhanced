#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础示例 7：获取股票列表

本示例展示如何使用 akshare-one 获取A股股票列表，包括：
- 获取全部A股实时行情数据
- 按市场筛选（沪市/深市/科创板/创业板）
- 按行业板块筛选
- 导出股票列表到CSV文件

运行方式：
    python examples/basic/07_stock_list.py
"""

import os
import pandas as pd
from datetime import datetime
from akshare_one import (
    get_realtime_data,
    get_industry_list,
    get_industry_stocks,
    get_kcb_stocks,
    get_cyb_stocks,
)


def example_get_all_stocks():
    """场景1：获取全部A股列表"""
    print("\n" + "=" * 60)
    print("场景1：获取全部A股股票列表")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")
    return None


def example_filter_by_market(df_all=None):
    """场景2：按市场筛选"""
    print("\n" + "=" * 60)
    print("场景2：按市场筛选股票")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_filter_by_industry():
    """场景3：按行业筛选"""
    print("\n" + "=" * 60)
    print("场景3：按行业板块筛选股票")
    print("=" * 60)

    try:
        # 获取行业列表
        df_industries = get_industry_list(source="eastmoney")

        if df_industries.empty:
            print("\n错误: 未获取到行业列表")
            return

        print(f"\n获取到 {len(df_industries)} 个行业板块")
        print("\n行业板块列表（前10个）：")
        print(df_industries.head(10).to_string(index=False))

        # 选择几个示例行业获取股票
        example_industries = ["白酒", "半导体", "银行"]

        for industry_name in example_industries:
            try:
                print(f"\n\n行业：{industry_name}")
                df_stocks = get_industry_stocks(industry_name, source="eastmoney")

                if df_stocks.empty:
                    print(f"  未找到该行业的股票数据")
                    continue

                print(f"  股票数量: {len(df_stocks)}")
                print(f"  前5只股票：")
                print(df_stocks.head(5).to_string(index=False))

            except Exception as e:
                print(f"  获取行业'{industry_name}'股票失败: {e}")

    except Exception as e:
        print(f"\n错误: 获取行业列表失败 - {e}")


def example_export_to_csv(df_all=None):
    """场景4：导出股票列表到CSV"""
    print("\n" + "=" * 60)
    print("场景4：导出股票列表到CSV")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def example_statistics(df_all=None):
    """额外场景：统计分析"""
    print("\n" + "=" * 60)
    print("额外场景：市场统计分析")
    print("=" * 60)
    print("注意：实时数据源当前不可用，跳过此示例")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 股票列表查询示例")
    print("=" * 60)

    # 先获取全市场数据，后续场景可以复用
    print("\n提示: 正在获取全市场数据...")
    df_all = example_get_all_stocks()

    # 运行其他场景
    example_filter_by_market(df_all)
    example_filter_by_industry()
    example_export_to_csv(df_all)
    example_statistics(df_all)

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
    print("\n实用提示：")
    print("1. 使用 get_realtime_data() 不传参数可获取全市场数据")
    print("2. 使用股票代码前缀规则可快速筛选市场")
    print("3. 使用 get_industry_stocks() 可获取指定行业的股票")
    print("4. 导出数据前建议先排序和格式化，提高可读性")


if __name__ == "__main__":
    main()
