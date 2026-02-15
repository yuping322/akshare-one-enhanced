#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观数据示例程序

本示例展示如何使用 akshare-one 的宏观数据模块获取和分析数据。

依赖：
- pandas

运行方式：
    python macro_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#macro
"""

from datetime import datetime, timedelta
import pandas as pd

# 导入模块
from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate,
)
from akshare_one.modules.macro.factory import MacroFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
    UpstreamChangedError,
)


def scenario_1_lpr_rate():
    """场景 1：监控 LPR 利率变化"""
    print("\n" + "=" * 80)
    print("场景 1：监控 LPR 利率变化")
    print("=" * 80)

    try:
        # 参数设置：获取最近一年的 LPR 利率数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print("正在获取 LPR 利率数据...")

        # 接口调用
        df = get_lpr_rate(start_date=start_date, end_date=end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近 10 条记录
        print("\nLPR 利率历史数据（最近 10 条）：")
        print(df.head(10).to_string(index=False))

        # 统计分析
        if len(df) > 0:
            latest = df.iloc[0]
            print(f"\n最新 LPR 利率（{latest['date']}）：")
            print(f"  1年期 LPR: {latest['lpr_1y']:.2f}%")
            print(f"  5年期 LPR: {latest['lpr_5y']:.2f}%")

            # 计算利率变化趋势
            if len(df) > 1:
                previous = df.iloc[1]
                lpr_1y_change = latest['lpr_1y'] - previous['lpr_1y']
                lpr_5y_change = latest['lpr_5y'] - previous['lpr_5y']

                print("\n较上次变化：")
                print(f"  1年期 LPR: {lpr_1y_change:+.2f}%")
                print(f"  5年期 LPR: {lpr_5y_change:+.2f}%")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期范围")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_pmi_index():
    """场景 2：追踪 PMI 指数"""
    print("\n" + "=" * 80)
    print("场景 2：追踪 PMI 指数")
    print("=" * 80)

    try:
        # 参数设置：获取最近一年的制造业 PMI 指数
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        pmi_type = "manufacturing"

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print(f"PMI 类型：{pmi_type}")
        print("正在获取制造业 PMI 指数数据...")

        # 接口调用
        df = get_pmi_index(start_date=start_date, end_date=end_date, pmi_type=pmi_type)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近 10 条记录
        print("\n制造业 PMI 指数历史数据（最近 10 条）：")
        print(df.head(10).to_string(index=False))

        # 统计分析
        if len(df) > 0:
            latest = df.iloc[0]
            print(f"\n最新 PMI 指数（{latest['date']}）：")
            print(f"  PMI 值: {latest['pmi_value']:.2f}")

            # 判断经济扩张或收缩
            if latest['pmi_value'] > 50:
                print("  经济状态: 扩张（PMI > 50）")
            elif latest['pmi_value'] < 50:
                print("  经济状态: 收缩（PMI < 50）")
            else:
                print("  经济状态: 持平（PMI = 50）")

            # 显示同比和环比变化
            if 'yoy' in df.columns and pd.notna(latest['yoy']):
                print(f"  同比变化: {latest['yoy']:+.2f}")
            if 'mom' in df.columns and pd.notna(latest['mom']):
                print(f"  环比变化: {latest['mom']:+.2f}")

            # 计算平均值
            avg_pmi = df['pmi_value'].mean()
            print(f"\n近一年平均 PMI: {avg_pmi:.2f}")

            # 统计扩张和收缩月份
            expansion_months = len(df[df['pmi_value'] > 50])
            contraction_months = len(df[df['pmi_value'] < 50])
            print(f"扩张月份数: {expansion_months}")
            print(f"收缩月份数: {contraction_months}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否为 YYYY-MM-DD，PMI 类型是否为 'manufacturing', 'non_manufacturing' 或 'caixin'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期范围")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_cpi_ppi_data():
    """场景 3：查询 CPI 和 PPI 数据"""
    print("\n" + "=" * 80)
    print("场景 3：查询 CPI 和 PPI 数据")
    print("=" * 80)

    try:
        # 参数设置：获取最近一年的通胀指标数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")

        # 获取 CPI 数据
        print("\n正在获取 CPI（居民消费价格指数）数据...")
        cpi_df = get_cpi_data(start_date=start_date, end_date=end_date)

        if not cpi_df.empty:
            print("\nCPI 数据（最近 10 条）：")
            print(cpi_df.head(10).to_string(index=False))

            # 统计分析 CPI
            if len(cpi_df) > 0:
                latest_cpi = cpi_df.iloc[0]
                print(f"\n最新 CPI 数据（{latest_cpi['date']}）：")
                if 'current' in cpi_df.columns and pd.notna(latest_cpi['current']):
                    print(f"  当月值: {latest_cpi['current']:.2f}")
                if 'yoy' in cpi_df.columns and pd.notna(latest_cpi['yoy']):
                    print(f"  同比涨幅: {latest_cpi['yoy']:+.2f}%")
                if 'mom' in cpi_df.columns and pd.notna(latest_cpi['mom']):
                    print(f"  环比涨幅: {latest_cpi['mom']:+.2f}%")
                if 'cumulative' in cpi_df.columns and pd.notna(latest_cpi['cumulative']):
                    print(f"  累计值: {latest_cpi['cumulative']:.2f}")

                # 计算平均同比涨幅
                if 'yoy' in cpi_df.columns:
                    avg_yoy = cpi_df['yoy'].mean()
                    print(f"\n近一年平均同比涨幅: {avg_yoy:.2f}%")
        else:
            print("CPI 数据为空")

        # 获取 PPI 数据
        print("\n正在获取 PPI（工业生产者出厂价格指数）数据...")
        ppi_df = get_ppi_data(start_date=start_date, end_date=end_date)

        if not ppi_df.empty:
            print("\nPPI 数据（最近 10 条）：")
            print(ppi_df.head(10).to_string(index=False))

            # 统计分析 PPI
            if len(ppi_df) > 0:
                latest_ppi = ppi_df.iloc[0]
                print(f"\n最新 PPI 数据（{latest_ppi['date']}）：")
                if 'current' in ppi_df.columns and pd.notna(latest_ppi['current']):
                    print(f"  当月值: {latest_ppi['current']:.2f}")
                if 'yoy' in ppi_df.columns and pd.notna(latest_ppi['yoy']):
                    print(f"  同比涨幅: {latest_ppi['yoy']:+.2f}%")
                if 'mom' in ppi_df.columns and pd.notna(latest_ppi['mom']):
                    print(f"  环比涨幅: {latest_ppi['mom']:+.2f}%")
                if 'cumulative' in ppi_df.columns and pd.notna(latest_ppi['cumulative']):
                    print(f"  累计值: {latest_ppi['cumulative']:.2f}")

                # 计算平均同比涨幅
                if 'yoy' in ppi_df.columns:
                    avg_yoy = ppi_df['yoy'].mean()
                    print(f"\n近一年平均同比涨幅: {avg_yoy:.2f}%")
        else:
            print("PPI 数据为空")

        # 通胀分析
        if not cpi_df.empty and not ppi_df.empty and len(cpi_df) > 0 and len(ppi_df) > 0:
            latest_cpi = cpi_df.iloc[0]
            latest_ppi = ppi_df.iloc[0]

            print("\n通胀指标分析：")
            if 'yoy' in cpi_df.columns and 'yoy' in ppi_df.columns:
                if pd.notna(latest_cpi['yoy']) and pd.notna(latest_ppi['yoy']):
                    print(f"  CPI 同比: {latest_cpi['yoy']:+.2f}%")
                    print(f"  PPI 同比: {latest_ppi['yoy']:+.2f}%")
                    print(f"  PPI-CPI 剪刀差: {latest_ppi['yoy'] - latest_cpi['yoy']:+.2f}%")

                    # 判断通胀状态
                    if latest_cpi['yoy'] > 3:
                        print("  通胀状态: 高通胀（CPI > 3%）")
                    elif latest_cpi['yoy'] > 2:
                        print("  通胀状态: 温和通胀（2% < CPI ≤ 3%）")
                    elif latest_cpi['yoy'] > 0:
                        print("  通胀状态: 低通胀（0% < CPI ≤ 2%）")
                    else:
                        print("  通胀状态: 通缩（CPI ≤ 0%）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期范围")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_4_m2_supply():
    """场景 4：监控货币供应量"""
    print("\n" + "=" * 80)
    print("场景 4：监控货币供应量")
    print("=" * 80)

    try:
        # 参数设置：获取最近一年的 M2 货币供应量数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print("正在获取 M2 货币供应量数据...")

        # 接口调用
        df = get_m2_supply(start_date=start_date, end_date=end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近 10 条记录
        print("\nM2 货币供应量历史数据（最近 10 条）：")
        # Only show date and yoy_growth_rate since m2_balance is not available
        display_df = df[['date', 'yoy_growth_rate']].copy()
        print(display_df.head(10).to_string(index=False))

        # 统计分析
        if len(df) > 0:
            latest = df.iloc[0]
            print(f"\n最新 M2 数据（{latest['date']}）：")
            print(f"  同比增长率: {latest['yoy_growth_rate']:+.2f}%")

            # 计算 M2 增长率变化趋势
            if len(df) > 1:
                previous = df.iloc[1]
                growth_rate_change = latest['yoy_growth_rate'] - previous['yoy_growth_rate']

                print("\n较上月变化：")
                print(f"  增长率变化: {growth_rate_change:+.2f}%")

            # 计算平均增长率
            avg_growth_rate = df['yoy_growth_rate'].mean()
            print(f"\n近一年平均同比增长率: {avg_growth_rate:.2f}%")

            # 判断货币政策倾向
            if latest['yoy_growth_rate'] > avg_growth_rate:
                print("货币政策倾向: 相对宽松（当前增长率高于平均水平）")
            elif latest['yoy_growth_rate'] < avg_growth_rate:
                print("货币政策倾向: 相对收紧（当前增长率低于平均水平）")
            else:
                print("货币政策倾向: 保持稳定（当前增长率接近平均水平）")

            # 显示 M2 增长率区间
            max_growth = df['yoy_growth_rate'].max()
            min_growth = df['yoy_growth_rate'].min()
            print(f"\n近一年增长率区间: {min_growth:.2f}% ~ {max_growth:.2f}%")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期范围")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_5_shibor_rate():
    """场景 5：追踪 Shibor 利率"""
    print("\n" + "=" * 80)
    print("场景 5：追踪 Shibor 利率")
    print("=" * 80)

    try:
        # 参数设置：获取最近一年的 Shibor 利率数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")
        print("正在获取 Shibor 利率数据...")

        # 接口调用
        df = get_shibor_rate(start_date=start_date, end_date=end_date)

        # 数据处理
        if df.empty:
            print("无数据返回")
            return

        # 结果展示：显示最近 10 条记录
        print("\nShibor 利率历史数据（最近 10 条）：")
        print(df.head(10).to_string(index=False))

        # 统计分析
        if len(df) > 0:
            latest = df.iloc[0]
            print(f"\n最新 Shibor 利率（{latest['date']}）：")

            # 显示各期限利率
            rate_columns = ['overnight', 'week_1', 'week_2', 'month_1', 'month_3', 'month_6', 'month_9', 'year_1']
            rate_names = {
                'overnight': '隔夜',
                'week_1': '1周',
                'week_2': '2周',
                'month_1': '1个月',
                'month_3': '3个月',
                'month_6': '6个月',
                'month_9': '9个月',
                'year_1': '1年'
            }

            for col in rate_columns:
                if col in df.columns and pd.notna(latest[col]):
                    print(f"  {rate_names[col]}: {latest[col]:.4f}%")

            # 计算利率变化趋势
            if len(df) > 1:
                previous = df.iloc[1]
                print("\n较上一交易日变化：")

                for col in rate_columns:
                    if col in df.columns and pd.notna(latest[col]) and pd.notna(previous[col]):
                        change = latest[col] - previous[col]
                        print(f"  {rate_names[col]}: {change:+.4f}%")

            # 计算平均利率
            print("\n近一年平均利率：")
            for col in rate_columns:
                if col in df.columns:
                    avg_rate = df[col].mean()
                    if pd.notna(avg_rate):
                        print(f"  {rate_names[col]}: {avg_rate:.4f}%")

            # 分析利率曲线形态
            if all(col in df.columns and pd.notna(latest[col]) for col in ['overnight', 'month_3', 'year_1']):
                overnight_rate = latest['overnight']
                month_3_rate = latest['month_3']
                year_1_rate = latest['year_1']

                print("\n利率曲线分析：")
                print(f"  短期利率（隔夜）: {overnight_rate:.4f}%")
                print(f"  中期利率（3个月）: {month_3_rate:.4f}%")
                print(f"  长期利率（1年）: {year_1_rate:.4f}%")

                # 判断利率曲线形态
                if year_1_rate > month_3_rate > overnight_rate:
                    print("  曲线形态: 正常（向上倾斜）")
                    print("  市场预期: 经济增长预期良好")
                elif year_1_rate < month_3_rate < overnight_rate:
                    print("  曲线形态: 倒挂（向下倾斜）")
                    print("  市场预期: 可能预示经济衰退风险")
                else:
                    print("  曲线形态: 平坦或不规则")
                    print("  市场预期: 市场观望情绪较重")

                # 计算期限利差
                term_spread = year_1_rate - overnight_rate
                print(f"  期限利差（1年-隔夜）: {term_spread:.4f}%")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据，请尝试其他日期范围")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except UpstreamChangedError as e:
        print(f"上游数据格式变化：{e}")
        print("提示：数据源格式可能已更新，请联系技术支持更新接口")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("宏观数据示例程序")
    print("=" * 80)

    # 场景 1：监控 LPR 利率变化
    scenario_1_lpr_rate()

    # 场景2：追踪 PMI 指数
    scenario_2_pmi_index()

    # 场景 3：查询 CPI 和 PPI 数据
    scenario_3_cpi_ppi_data()

    # 场景 4：监控货币供应量
    scenario_4_m2_supply()

    # 场景 5：追踪 Shibor 利率
    scenario_5_shibor_rate()

    # 场景 6：使用备用数据源
    scenario_6_multi_source_example()


def scenario_6_multi_source_example():
    """场景 6：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 6：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = MacroFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = MacroFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询时间范围：{start_date} 至 {end_date}")

        # 通过 provider 获取数据
        df = sina_provider.get_lpr_rate(start_date, end_date)

        if df.empty:
            print("无 LPR 数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
