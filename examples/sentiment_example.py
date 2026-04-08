#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场情绪示例程序

本示例展示如何使用 akshare-one 的市场情绪模块获取热门排名和技术指标。

依赖：
- pandas

运行方式：
    python sentiment_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#sentiment
"""

from akshare_one.modules.sentiment import (
    get_hot_rank,
    compute_fed_model,
    compute_crowding_ratio,
    compute_graham_index,
    compute_below_net_ratio,
)
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_hot_rank():
    """场景 1：获取热门股票排名"""
    print("\n" + "=" * 80)
    print("场景 1：获取热门股票排名")
    print("=" * 80)

    try:
        print("\n正在获取热门股票排名...")

        df = get_hot_rank()

        if df.empty:
            print("无热门排名数据返回")
            return

        print(f"\n热门股票排名（共 {len(df)} 只）：")
        print(df.head(20).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_fed_model():
    """场景 2：计算 FED 模型"""
    print("\n" + "=" * 80)
    print("场景 2：计算 FED 模型")
    print("=" * 80)

    try:
        print("\n正在计算 FED 模型估值...")

        result = compute_fed_model(index_code="000300")

        if "fed" in result and result["fed"] != 0:
            print(f"\nFED 模型结果：")
            print(f"  FED 值：{result['fed']:.4f}")
            print(f"  PE 倒数：{1 / result['pe']:.4f}")
            print(f"  沪深300 PE：{result['pe']:.2f}")
            print(f"  债券收益率：{result['bond_rate']:.4f}")

            if result["fed"] > 0:
                print("  解读：股票相对债券更具吸引力")
            else:
                print("  解读：债券相对股票更具吸引力")
        else:
            print("  当前无法获取 FED 模型数据（数据源问题）")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_crowding_ratio():
    """场景 3：计算市场拥挤度"""
    print("\n" + "=" * 80)
    print("场景 3：计算市场拥挤度")
    print("=" * 80)

    try:
        print("\n正在计算市场拥挤度...")

        result = compute_crowding_ratio()

        if "ratio" in result and result["ratio"] != 0:
            print(f"\n市场拥挤度结果：")
            print(f"  成交额集中度：{result['ratio']:.4f} ({result['ratio'] * 100:.2f}%)")
            print(f"  总成交额：{result.get('total', 0):,.2f}")

            if result["ratio"] > 0.4:
                print("  解读：市场成交集中度高，可能存在局部泡沫")
            elif result["ratio"] > 0.3:
                print("  解读：市场成交分布较为集中")
            else:
                print("  解读：市场成交分布较为均衡")
        else:
            print("  当前无法获取市场拥挤度数据（数据源问题）")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_graham_index():
    """场景 4：计算格雷厄姆指数"""
    print("\n" + "=" * 80)
    print("场景 4：计算格雷厄姆指数")
    print("=" * 80)

    try:
        print("\n正在计算格雷厄姆指数...")

        result = compute_graham_index(index_code="000300")

        if "graham" in result and result["graham"] != 0:
            print(f"\n格雷厄姆指数结果：")
            print(f"  指数值：{result['graham']:.4f}")

            if result["graham"] > 1:
                print("  解读：股票被低估，适合价值投资")
            elif result["graham"] > 0.5:
                print("  解读：估值处于合理区间")
            else:
                print("  解读：股票被高估")
        else:
            print("  当前无法获取格雷厄姆指数数据（数据源问题）")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_5_below_net_ratio():
    """场景 5：计算破净股比例"""
    print("\n" + "=" * 80)
    print("场景 5：计算破净股比例")
    print("=" * 80)

    try:
        print("\n正在计算破净股比例...")

        result = compute_below_net_ratio()

        if "ratio" in result and result["ratio"] != 0:
            print(f"\n破净股统计结果：")
            print(f"  破净股数量：{result.get('count', 0)} 只")
            print(f"  市场总股票数：{result.get('total', 0)} 只")
            print(f"  破净股比例：{result['ratio']:.4f} ({result['ratio'] * 100:.2f}%)")

            if result["ratio"] > 0.2:
                print("  解读：市场整体估值偏低，可能处于底部区域")
            elif result["ratio"] > 0.1:
                print("  解读：市场估值适中")
            else:
                print("  解读：市场整体估值偏高")
        else:
            print("  当前无法获取破净股数据（数据源问题）")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("市场情绪示例程序")
    print("=" * 80)

    scenario_1_hot_rank()
    scenario_2_fed_model()
    scenario_3_crowding_ratio()
    scenario_4_graham_index()
    scenario_5_below_net_ratio()

    print("\n" + "=" * 80)
    print("示例程序运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
